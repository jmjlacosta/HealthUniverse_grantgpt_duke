from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import zipfile
from io import BytesIO
from typing import Literal, Annotated
import shutil

from create_query import create_jsonl_entry, generate_jsonl_file

app = FastAPI(
    title="TrialGPT Tool: Duke Clinical Studies",
    description="API for matching patients to clinical trials using Large Language Models",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# def ensure_directories():
#     """Create necessary directories for processing"""
#     os.makedirs("dataset/data", exist_ok=True)
#     os.makedirs("results", exist_ok=True)

def save_uploaded_file(file_content: bytes, save_path: str):
    """Save uploaded file to specified path"""
    with open(save_path, "wb") as f:
        f.write(file_content)

def clear_corpus_folder():
    """Clear the dataset/data directory"""
    if os.path.exists("dataset/data"):
        for file in os.listdir("dataset/data"):
            file_path = os.path.join("dataset/data", file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

def run_pipeline(k: int, bm25_weight: float, medcpt_weight: float):
    """Run the complete TrialGPT pipeline"""
    steps = [
        (["python", "trialgpt_retrieval/keyword_generation.py"], "Keyword generation failed"),
        (["python", "trialgpt_retrieval/hybrid_fusion_retrieval.py", "data", "gpt-4o",
          str(k), str(int(bm25_weight)), str(int(medcpt_weight))], "Hybrid fusion retrieval failed"),
        (["python", "trialgpt_retrieval/retrieval.py", "dataset/data/qid2nctids_results.json"],
         "Retrieved trials failed"),
        (["python", "trialgpt_matching/run_matching.py", "data", "gpt-4o"], "Matching failed"),
        (["python", "trialgpt_matching/generate_trial_info.py", "data"], "Trial info generation failed"),
        (["python", "trialgpt_ranking/run_aggregation.py", "data", "gpt-4o",
          "dataset/data/matching_results.json"], "Aggregation failed"),
        (["python", "trialgpt_ranking/rank_results.py", "dataset/data/matching_results.json",
          "dataset/data/aggregation_results.json"], "Final ranking failed")
    ]

    for command, error_message in steps:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"{error_message}: {result.stderr}")

corpus_base_path = "duke_corpus"

@app.post("/process-trials")
async def process_trials(
    corpus: Annotated[Literal["Duke - All Trials", "Duke - Oncology Trials", "Duke - COPD Trials"], Form(..., description="Select the clinical trial dataset you want to process: 'All Trials' (comprehensive dataset), 'Oncology Trials' (cancer-related trials), or 'COPD Trials' (chronic obstructive pulmonary disease-related trials)")] = "Duke - All Trials",
    patient_id: Annotated[str, Form(..., description="Unique identifier for the patient (e.g., 'patient123')")] = "id",
    queries: Annotated[str, Form(..., description="Narrative or medical history of the patient to be processed")] = "query",
    k: Annotated[str, Form(..., description="Number of results to return (default is 20)")] = "20",
):

    try: 
        k = int(k)
    except:
        k = 20
    # ensure_directories()
    clear_corpus_folder()

    bm25_weight = 1.0
    medcpt_weight = 1.0

    # Map corpus selection to folder
    corpus_mapping = {
        "Duke - All Trials": "all",
        "Duke - Oncology Trials": "onco",
        "Duke - COPD Trials": "copd"
    }

    #determine folder name
    selected_corpus_folder = corpus_mapping[corpus]

    # path to the corpus.jsonl file
    corpus_file_path = os.path.join(corpus_base_path, selected_corpus_folder, "corpus.jsonl")

    #  copy corpus file into the dataset/data folder
    try:
        shutil.copy(corpus_file_path, "dataset/data/corpus.jsonl")
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Corpus file not found")


    # Save queries to dataset folder as JSONL
    queries_jsonl_bytes = generate_jsonl_file(patient_id, queries)  # Using the queries string

    # Save the generated queries file
    save_uploaded_file(queries_jsonl_bytes, "dataset/data/queries.jsonl")

    try:
        # Run the complete pipeline
        await run_pipeline(k, bm25_weight, medcpt_weight)

        # Read ranking results
        ranking_path = "dataset/data/1_FINAL_ranking_results.txt"
        with open(ranking_path, "r") as f:
            rankings = f.read()

        # Create ZIP file with all data
        zip_path = "dataset/data/results.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk("dataset/data"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "dataset/data")
                    zipf.write(file_path, arcname)

        # Return rankings and a download link for the ZIP file
        return {
            "rankings": rankings,
            "download_url": "/download-results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-results")
async def download_results():
    """Endpoint to download the ZIP file"""
    zip_path = "dataset/data/results.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Results file not found")
    return FileResponse(zip_path, filename="results.zip", media_type="application/zip")

# @app.on_event("startup")
# async def startup_event():
#     """Initialize necessary directories on startup"""
#     ensure_directories()
