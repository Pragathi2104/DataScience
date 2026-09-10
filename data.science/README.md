# Meatwise

Frontend-first Flask dashboard for a Meat Analysis System using Python and data science workflows.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The current analysis endpoint uses a transparent rule-based demo in `app.py`; replace it with the trained model and persistence layer when those are ready.
