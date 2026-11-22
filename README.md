# Project 1 (P1): CLI AI Helper with Tool Calling (Python + Gemini)

A lightweight, CLI-only Python assistant built for Quayutec onboarding. It demonstrates:
- Explicit multi-step tool-calling loop (`model -> tool -> result -> model`)
- Three local/free Python tools (`search_notes`, `add_days`, `get_weather_info`)
- Structured final output validated with **Pydantic v2**
- Per-question token usage reporting

## Project Structure

```text
project-1/
├── agent.py           # CLI entrypoint, plain chat check, tool-calling loop, Pydantic validation
├── tools.py           # 3 local/free tools + Gemini FunctionDeclaration schemas
├── schemas.py         # Pydantic BaseModel (AgentResponse) for structured output
├── notes/             # Sample local markdown notes searched by search_notes()
│   ├── onboarding.md
│   ├── meetings.md
│   └── tech_stack.md
├── requirements.txt   # Python dependencies
├── .env.example       # Template for environment variables
├── .gitignore
└── README.md
```

## Setup (Clone & Run)

1. **Clone the repository** and enter the project folder:
   ```bash
   git clone <your-repo-url>
   cd project-1
   ```

2. **Create and activate a virtual environment** (Python 3.11+ recommended):
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your free Google AI Studio API key**:
   - Get a free key from [Google AI Studio](https://aistudio.google.com/apikey).
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set `GEMINI_API_KEY=your_actual_key`.

## Usage

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
Type `exit` or `quit` to leave.
