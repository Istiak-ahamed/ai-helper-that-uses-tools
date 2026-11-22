# Project 1 (P1): AI Helper That Uses Tools (Python + Gemini)

A lightweight, CLI-only Python assistant built for Quayutec onboarding. It demonstrates:
- Explicit multi-step tool-calling loop (`model -> tool -> result -> model`)
- Three local/free Python tools (`search_notes`, `add_days`, `get_weather_info`)
- Structured final output validated with **Pydantic v2**
- Per-question token usage reporting

## Project Structure

```text
ai-helper-that-uses-tools/
├── agent.py           # CLI entrypoint, plain chat check, tool-calling loop, Pydantic validation
├── tools.py           # 3 local/free tools + Gemini FunctionDeclaration schemas
├── schemas.py         # Pydantic BaseModel (AgentResponse) for structured output
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore         # Excludes .env, .venv/, __pycache__/
├── notes/             # Optional local .md/.txt notes searched by search_notes()
│   ├── onboarding.md
│   ├── meetings.md
│   └── tech_stack.md
└── README.md
```

### About `notes/`
The `notes/` folder holds local Markdown (`.md`) and text (`.txt`) files that the `search_notes()` tool searches when you ask questions about your onboarding, schedule, or tech stack. It is **optional**—if `notes/` is missing or empty, `search_notes()` returns an empty result cleanly without crashing, and `add_days()` / `get_weather_info()` continue to work normally.

---

## Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Istiak-ahamed/ai-helper-that-uses-tools.git
cd ai-helper-that-uses-tools
```

### 2. Install dependencies

#### Option A: With a Virtual Environment (Recommended)
Create the virtual environment:
```bash
python -m venv .venv
```

Activate it based on your terminal:
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (Git Bash):**
  ```bash
  source .venv/Scripts/activate
  ```
- **Windows (Command Prompt):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

Install dependencies inside `.venv`:
```bash
pip install -r requirements.txt
```

#### Option B: Without a Virtual Environment
If you prefer to install packages directly into your global/user Python environment:
```bash
pip install -r requirements.txt
```
*(You can then run `python agent.py` directly without activating any `.venv`.)*

---

### 3. Configure your Gemini API key
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Copy `.env.example` to `.env`:
   - **Bash / macOS / Linux:**
     ```bash
     cp .env.example .env
     ```
   - **PowerShell:**
     ```powershell
     Copy-Item .env.example .env
     ```
3. Open `.env` and set your key (and optionally the model):
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   ```
   *(If `GEMINI_MODEL` is not set, it defaults to `gemini-3.8-flash` with automatic fallback to `gemini-3.5-flash-lite` on `503` overload.)*

---

## Running the CLI

### 1. Plain Chat Check (No Tools)
Verify your API key and connectivity:
```bash
python agent.py --plain "Say hello in one sentence."
```

### 2. Single-Question Tool-Calling Mode
Run a multi-tool question from the command line:
```bash
python agent.py "When is my Quayutec onboarding start date, what date is 7 days after it, and what is the weather in Dhaka?"
```

### 3. Interactive CLI Mode
Start an interactive session:
```bash
python agent.py
```
Type your question and press Enter. Type `exit` or `quit` to stop.
