import argparse
import os
import sys
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas import AgentResponse
from tools import TOOL_DECLARATIONS, execute_tool

SYSTEM_INSTRUCTION = (
    "You are a helpful CLI assistant for Quayutec onboarding. "
    "Use the provided tools whenever you need information from local notes, "
    "date calculations, or weather data. "
    "Once you have all required information, provide a clear and accurate final answer."
)


def create_client() -> tuple[genai.Client, str]:
    """Load environment variables and initialize the Gemini API client."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_google_ai_studio_api_key_here":
        print(
            "Error: GEMINI_API_KEY is not set.\n"
            "Copy .env.example to .env and add your free Google AI Studio key.",
            file=sys.stderr,
        )
        sys.exit(1)

    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
    return genai.Client(api_key=api_key), model_name


def accumulate_tokens(totals: dict[str, int], usage: Any) -> None:
    """Add token counts from a single API response to the running totals."""
    if not usage:
        return
    totals["prompt"] += getattr(usage, "prompt_token_count", 0) or 0
    totals["candidates"] += getattr(usage, "candidates_token_count", 0) or 0
    totals["total"] += getattr(usage, "total_token_count", 0) or 0


def print_token_usage(totals: dict[str, int]) -> None:
    """Print per-question token usage summary."""
    print(
        f"\n[Token Usage] prompt={totals['prompt']} | "
        f"output={totals['candidates']} | total={totals['total']}"
    )


def run_plain_chat(client: genai.Client, model: str, question: str) -> None:
    """Plain chat check without tools, useful for verifying API connectivity."""
    response = client.models.generate_content(model=model, contents=question)
    totals = {"prompt": 0, "candidates": 0, "total": 0}
    accumulate_tokens(totals, response.usage_metadata)

    print("\n[Plain Chat Response]")
    print(response.text or "(empty response)")
    print_token_usage(totals)


def run_tool_agent(
    client: genai.Client, model: str, question: str, max_steps: int = 10
) -> AgentResponse:
    """Execute the explicit model -> tool -> result -> model loop with Pydantic validation."""
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=question)])
    ]
    totals = {"prompt": 0, "candidates": 0, "total": 0}
    tools_used: list[str] = []

    for step in range(1, max_steps + 1):
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[TOOL_DECLARATIONS],
            ),
        )
        accumulate_tokens(totals, response.usage_metadata)

        function_calls = response.function_calls
        if not function_calls:
            # No more tool calls: append final model turn and break out of loop.
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)
            break

        # Append the model's tool-call turn to conversation history.
        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)

        tool_response_parts: list[types.Part] = []
        for call in function_calls:
            tool_name = call.name
            tool_args = dict(call.args) if call.args else {}
            print(f"[Step {step}] Tool Call: {tool_name}({tool_args})")

            result = execute_tool(tool_name, tool_args)
            print(f"[Step {step}] Tool Result: {result}")

            if tool_name not in tools_used:
                tools_used.append(tool_name)

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response=result,
                )
            )

        contents.append(types.Content(role="user", parts=tool_response_parts))
    else:
        print(f"[Warning] Reached max_steps={max_steps} before final answer.")

    # Request structured JSON matching AgentResponse and validate with Pydantic.
    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        "Format your final answer as JSON matching the required schema. "
                        f"Tools used in this session: {tools_used}."
                    )
                )
            ],
        )
    )
    structured_response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AgentResponse,
        ),
    )
    accumulate_tokens(totals, structured_response.usage_metadata)

    validated = AgentResponse.model_validate_json(structured_response.text)
    print("\n[Validated Final Output (Pydantic)]")
    print(validated.model_dump_json(indent=2))
    print_token_usage(totals)
    return validated


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quayutec P1 — CLI AI Assistant with Gemini Tool Calling & Pydantic"
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Single question to run. Omit to start interactive CLI mode.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Run a plain chat check without tools.",
    )
    args = parser.parse_args()

    client, model = create_client()

    if args.question:
        if args.plain:
            run_plain_chat(client, model, args.question)
        else:
            run_tool_agent(client, model, args.question)
        return

    print(f"Quayutec P1 CLI Assistant (model: {model})")
    print("Type your question and press Enter. Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if args.plain:
            run_plain_chat(client, model, user_input)
        else:
            run_tool_agent(client, model, user_input)
        print()


if __name__ == "__main__":
    main()
