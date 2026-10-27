# Chilipir — MVP

Private ChatGPT assistant backend for evaluating **Artă** and **Foto** OLX listings in Romania.

## Current status
- FastAPI skeleton and evaluation endpoint.
- **No live OLX ingestion yet.** Automatic collection must use an authorized source.
- Discount score is indicative only; user-supplied reference prices are not validated.
- No hourly schedule or ChatGPT integration enabled yet.

## Local setup
```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Endpoints: `GET /health`, `POST /evaluate`, `GET /deals`.

## Next steps
1. Confirm lawful/authorized OLX listing access or user-provided links.
2. Add persistent database and comparable sold-price evidence.
3. Add scheduled jobs, notifications, authentication and MCP adapter.
4. Keep credentials in environment secrets, never in Git.
