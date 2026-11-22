from typing import Literal, Optional
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """Structured final answer returned by the CLI assistant."""

    answer: str = Field(
        description="Clear, concise final answer to the user's question based on tool outputs."
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="Names of the tools invoked to answer the question.",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level in the final answer."
    )
    follow_up_suggestion: Optional[str] = Field(
        default=None,
        description="Optional helpful next step or follow-up question for the user.",
    )
