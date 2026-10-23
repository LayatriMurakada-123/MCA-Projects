# AI Chatbot for ICET Rank and College Prediction System

## Technologies
- Python + Flask
- HTML5
- CSS3
- JavaScript
- SQL/SQLite
- REST APIs
- Agentic AI-style multi-agent orchestration

## Agent architecture

1. Rank Agent — converts an ICET score into an indicative rank band.
2. College Matching Agent — compares rank with college cutoff data.
3. Preference Agent — considers course, fee budget and city.
4. Explanation Agent — produces a simple explanation.
5. Agent Orchestrator — coordinates all agents.

This project is designed as a college academic project. It does not claim to reproduce the official ICET ranking algorithm.

## Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py
```

Open:

http://127.0.0.1:5000

The database is created automatically at `database/icet_predictor.db`.

## REST APIs

GET `/api/colleges`

POST `/api/predict`

Example:
```json
{
  "score": 125,
  "category": "OC",
  "region": "AU",
  "course": "MBA",
  "city": "Visakhapatnam",
  "max_fee": 55000
}
```

POST `/api/chat`

Example:
```json
{
  "message": "My score is 125"
}
```

## Important
The sample college and cutoff values are demonstration data. Replace them with verified official/current counselling data before using the application for real admission decisions.
