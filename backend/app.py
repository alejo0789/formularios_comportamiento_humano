"""
Backend API for Multi-Questionnaire System
Supports multiple questionnaires loaded from JSON files
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
import uuid
import glob

# Paths
BACKEND_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
QUESTIONNAIRES_DIR = os.path.join(BACKEND_DIR, "questionnaires")
DATA_DIR = os.path.join(BACKEND_DIR, "data")

app = FastAPI(
    title="Sistema de Cuestionarios",
    description="API for managing multiple questionnaires and responses",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QuestionResponse(BaseModel):
    question_id: int
    response_value: int

class SurveySubmission(BaseModel):
    questionnaire_id: str
    respondent_name: Optional[str] = None
    respondent_email: Optional[str] = None
    department: Optional[str] = None
    responses: List[QuestionResponse]

# Helper functions
def ensure_dirs():
    """Ensure data and questionnaires directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(QUESTIONNAIRES_DIR, exist_ok=True)

def load_questionnaire(questionnaire_id: str) -> Dict[str, Any]:
    """Load a questionnaire by ID"""
    file_path = os.path.join(QUESTIONNAIRES_DIR, f"{questionnaire_id}.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Questionnaire '{questionnaire_id}' not found")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_questionnaires() -> List[Dict[str, Any]]:
    """Get list of all available questionnaires"""
    ensure_dirs()
    questionnaires = []
    
    for file_path in glob.glob(os.path.join(QUESTIONNAIRES_DIR, "*.json")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questionnaires.append({
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "version": data.get("version"),
                    "icon": data.get("icon", "📋"),
                    "color": data.get("color", "#6366f1"),
                    "question_count": len(data.get("questions", []))
                })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading questionnaire {file_path}: {e}")
    
    return questionnaires

def get_responses_file(questionnaire_id: str) -> str:
    """Get the responses file path for a questionnaire"""
    ensure_dirs()
    return os.path.join(DATA_DIR, f"responses_{questionnaire_id}.json")

def load_responses(questionnaire_id: str) -> List[dict]:
    """Load all saved responses for a questionnaire"""
    file_path = get_responses_file(questionnaire_id)
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_response(questionnaire_id: str, response_data: dict):
    """Save a new response for a questionnaire"""
    file_path = get_responses_file(questionnaire_id)
    responses = load_responses(questionnaire_id)
    responses.append(response_data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

# API Endpoints
@app.get("/api/questionnaires")
async def list_questionnaires():
    """Get all available questionnaires"""
    questionnaires = get_all_questionnaires()
    return {
        "questionnaires": questionnaires,
        "total": len(questionnaires)
    }

@app.get("/api/questionnaires/{questionnaire_id}")
async def get_questionnaire(questionnaire_id: str):
    """Get a specific questionnaire with its questions and options"""
    data = load_questionnaire(questionnaire_id)
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "version": data.get("version"),
        "icon": data.get("icon", "📋"),
        "color": data.get("color", "#6366f1"),
        "estimated_time": data.get("estimated_time"),
        "options": data.get("options", []),
        "questions": data.get("questions", []),
        "sections": data.get("sections", []),
        "conditional_questions": data.get("conditional_questions", []),
        "total_questions": len(data.get("questions", []))
    }

@app.post("/api/submit")
async def submit_survey(submission: SurveySubmission):
    """Submit survey responses"""
    # Load questionnaire to validate
    questionnaire = load_questionnaire(submission.questionnaire_id)
    
    valid_question_ids = {q["id"] for q in questionnaire.get("questions", [])}
    valid_response_values = {opt["value"] for opt in questionnaire.get("options", [])}
    
    # Get non-conditional question IDs (required questions)
    required_question_ids = {q["id"] for q in questionnaire.get("questions", []) if not q.get("conditional", False)}
    
    # Validate responses
    for response in submission.responses:
        if response.question_id not in valid_question_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid question ID: {response.question_id}"
            )
        if response.response_value not in valid_response_values:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid response value: {response.response_value}"
            )
    
    # Check all required (non-conditional) questions are answered
    answered_ids = {r.question_id for r in submission.responses}
    missing_required = required_question_ids - answered_ids
    if missing_required:
        raise HTTPException(
            status_code=400,
            detail=f"Missing responses for required questions: {sorted(missing_required)}"
        )
    
    # Create response record
    response_id = str(uuid.uuid4())
    questions_dict = {q["id"]: q for q in questionnaire.get("questions", [])}
    options_dict = {opt["value"]: opt for opt in questionnaire.get("options", [])}
    
    response_data = {
        "id": response_id,
        "submitted_at": datetime.now().isoformat(),
        "respondent_name": submission.respondent_name,
        "respondent_email": submission.respondent_email,
        "department": submission.department,
        "responses": [
            {
                "question_id": r.question_id,
                "question_text": questions_dict[r.question_id]["text"],
                "response_value": r.response_value,
                "response_label": options_dict[r.response_value]["label"]
            }
            for r in submission.responses
        ]
    }
    
    # Save to file
    save_response(submission.questionnaire_id, response_data)
    
    return {
        "success": True,
        "message": "Encuesta enviada exitosamente",
        "submission_id": response_id
    }

@app.get("/api/responses/{questionnaire_id}")
async def get_all_responses(questionnaire_id: str):
    """Get all saved responses for a questionnaire"""
    # Verify questionnaire exists
    load_questionnaire(questionnaire_id)
    
    responses = load_responses(questionnaire_id)
    return {
        "questionnaire_id": questionnaire_id,
        "responses": responses,
        "total": len(responses)
    }

@app.get("/api/statistics/{questionnaire_id}")
async def get_statistics(questionnaire_id: str):
    """Get survey statistics for a questionnaire"""
    questionnaire = load_questionnaire(questionnaire_id)
    responses = load_responses(questionnaire_id)
    
    if not responses:
        return {
            "questionnaire_id": questionnaire_id,
            "questionnaire_name": questionnaire.get("name"),
            "total_responses": 0,
            "question_stats": {},
            "options": questionnaire.get("options", [])
        }
    
    # Calculate statistics per question
    question_stats = {}
    options = questionnaire.get("options", [])
    option_values = [opt["value"] for opt in options]
    
    for question in questionnaire.get("questions", []):
        q_id = question["id"]
        values = []
        for response in responses:
            for r in response["responses"]:
                if r["question_id"] == q_id:
                    values.append(r["response_value"])
        
        if values:
            avg = sum(values) / len(values)
            distribution = {v: values.count(v) for v in option_values}
            
            question_stats[q_id] = {
                "question_text": question["text"],
                "category": question.get("category", ""),
                "average": round(avg, 2),
                "total_responses": len(values),
                "distribution": distribution
            }
    
    return {
        "questionnaire_id": questionnaire_id,
        "questionnaire_name": questionnaire.get("name"),
        "total_responses": len(responses),
        "question_stats": question_stats,
        "options": questionnaire.get("options", [])
    }

# Serve frontend static files
@app.get("/")
async def serve_index():
    """Serve the questionnaire selector page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/encuesta/{questionnaire_id}")
async def serve_survey(questionnaire_id: str):
    """Serve the survey page for a specific questionnaire"""
    return FileResponse(os.path.join(FRONTEND_DIR, "encuesta.html"))

@app.get("/resultados/{questionnaire_id}")
async def serve_results(questionnaire_id: str):
    """Serve the results page for a specific questionnaire"""
    return FileResponse(os.path.join(FRONTEND_DIR, "resultados.html"))

# Legacy routes for backwards compatibility
@app.get("/encuesta")
async def serve_survey_legacy():
    """Redirect to selector if no questionnaire specified"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/resultados")
async def serve_results_legacy():
    """Redirect to selector if no questionnaire specified"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Mount static files (CSS, JS) - must be after API routes
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    ensure_dirs()
    print("\n" + "="*60)
    print("🚀 Sistema de Cuestionarios iniciado!")
    print("="*60)
    print("\n📋 SELECTOR DE CUESTIONARIOS:")
    print("   http://localhost:8000/")
    print("\n📝 ENCUESTA (ejemplo):")
    print("   http://localhost:8000/encuesta/estres")
    print("\n📊 RESULTADOS (ejemplo):")
    print("   http://localhost:8000/resultados/estres")
    print("\n💡 Agrega nuevos cuestionarios en:")
    print(f"   {QUESTIONNAIRES_DIR}")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
