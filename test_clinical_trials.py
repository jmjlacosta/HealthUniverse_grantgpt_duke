from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLINICAL_TRIALS_API = "https://clinicaltrials.gov/api/query/full_studies?expr=COPD&min_rnk=1&max_rnk=10&fmt=json"

@app.get("/test-clinical-trials")
async def test_clinical_trials():
    try:
        response = requests.get(CLINICAL_TRIALS_API, timeout=10)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "json": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {"error": str(e)}
