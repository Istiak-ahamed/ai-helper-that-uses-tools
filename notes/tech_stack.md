# Tech Stack Guidelines

- Language: Python 3.11+
- LLM SDK: google-genai (official Google Gen AI SDK)
- Validation: Pydantic v2 BaseModel
- Target Hardware: Lightweight CLI-only (16GB RAM CPU/iGPU friendly, no web UI)
- Environment: Load secrets via python-dotenv from .env (never hardcode keys)
