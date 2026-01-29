"""
Backend API for Multi-Questionnaire System
Supports multiple questionnaires loaded from JSON files
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
import uuid
import glob
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BACKEND_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
QUESTIONNAIRES_DIR = os.path.join(BACKEND_DIR, "questionnaires")
DATA_DIR = os.path.join(BACKEND_DIR, "data")

app = FastAPI(
    title="Sistema de Cuestionarios",
    description="API for managing multiple questionnaires and responses",
    version="2.0.0",
    root_path="/cuestionarios"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
# Sequence of questionnaires for the linear flow
SEQUENCE = ["datos-generales", "estres", "extralaborales", "intralaborales-a", "intralaborales-b"]

# ==========================================
# MODELS
# ==========================================

class Session(BaseModel):
    cedula: str
    name: Optional[str] = None
    completed_forms: List[str] = []
    current_step: str = "datos-generales"
    last_active: str

class QuestionResponse(BaseModel):
    question_id: int
    response_value: int


class SurveySubmission(BaseModel):
    questionnaire_id: str
    respondent_cedula: Optional[str] = None
    respondent_name: Optional[str] = None
    respondent_email: Optional[str] = None
    department: Optional[str] = None
    responses: List[QuestionResponse]

class FormSubmission(BaseModel):
    form_id: str
    submitted_at: Optional[str] = None
    data: Dict[str, Any]

# Helper functions
def ensure_dirs():
    """Ensure data and questionnaires directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(QUESTIONNAIRES_DIR, exist_ok=True)

def get_sessions_file() -> str:
    """Get the sessions file path"""
    ensure_dirs()
    return os.path.join(DATA_DIR, "sessions.json")

def load_sessions() -> Dict[str, dict]:
    """Load all sessions"""
    file_path = get_sessions_file()
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_session(session_data: dict):
    """Save/Update a session"""
    file_path = get_sessions_file()
    sessions = load_sessions()
    
    # Update specific session
    sessions[session_data["cedula"]] = session_data
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def get_next_step(completed_forms: List[str]) -> str:
    """Determine the next step based on completed starts"""
    for step in SEQUENCE:
        if step not in completed_forms:
            return step
    return "completed"

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

def get_form_responses_file(form_id: str) -> str:
    """Get the responses file path for a form"""
    ensure_dirs()
    return os.path.join(DATA_DIR, f"form_{form_id}.json")

def load_form_responses(form_id: str) -> List[dict]:
    """Load all saved responses for a form"""
    file_path = get_form_responses_file(form_id)
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_form_response(form_id: str, response_data: dict):
    """Save a new response for a form"""
    file_path = get_form_responses_file(form_id)
    responses = load_form_responses(form_id)
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
        "short_name": data.get("short_name"),
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
        "respondent_cedula": submission.respondent_cedula,
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
    
    # --- SESSION UPDATE LOGIC ---
    if submission.respondent_cedula:
        sessions = load_sessions()
        existing_session = sessions.get(submission.respondent_cedula)
        
        if existing_session:
            completed = set(existing_session.get("completed_forms", []))
            completed.add(submission.questionnaire_id)
            
            existing_session["completed_forms"] = list(completed)
            existing_session["last_active"] = datetime.now().isoformat()
            
            # Determine next step
            next_step = get_next_step(list(completed))
            existing_session["current_step"] = next_step
            
            save_session(existing_session)
            
            return {
                "success": True,
                "message": "Encuesta enviada exitosamente",
                "submission_id": response_id,
                "next_step": next_step
            }
    
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

@app.post("/api/submit-form")
async def submit_form(submission: FormSubmission):
    """Submit form data (datos generales)"""
    response_id = str(uuid.uuid4())
    
    response_data = {
        "id": response_id,
        "submitted_at": submission.submitted_at or datetime.now().isoformat(),
        "data": submission.data
    }
    
    # Save to file
    save_form_response(submission.form_id, response_data)
    
    # --- SESSION UPDATE LOGIC ---
    if submission.form_id == "datos-generales":
        cedula = submission.data.get("numero_identificacion")
        nombre = submission.data.get("nombre_completo")
        
        if cedula:
            sessions = load_sessions()
            existing_session = sessions.get(cedula, {})
            
            # Merge completed forms
            completed = set(existing_session.get("completed_forms", []))
            completed.add(submission.form_id)
            
            # Logic for Intralaboral Form Selection
            # If has personnel (Si) -> Do Intralaboral A (Skip B)
            # If no personnel (No) -> Do Intralaboral B (Skip A)
            personal_cargo = submission.data.get("tiene_personal_cargo")
            
            if personal_cargo == "si":
                completed.add("intralaborales-b")
                if "intralaborales-a" in completed:
                    completed.remove("intralaborales-a")
            elif personal_cargo == "no":
                completed.add("intralaborales-a")
                if "intralaborales-b" in completed:
                    completed.remove("intralaborales-b")
            
            new_session = {
                "cedula": cedula,
                "name": nombre or existing_session.get("name"),
                "completed_forms": list(completed),
                "last_active": datetime.now().isoformat(),
            }
            # Determine next step (re-calculation)
            new_session["current_step"] = get_next_step(new_session["completed_forms"])
            
            save_session(new_session)
            
            return {
                "success": True,
                "message": "Datos guardados exitosamente",
                "submission_id": response_id,
                "next_step": new_session["current_step"]
            }

    return {
        "success": True,
        "message": "Datos guardados exitosamente",
        "submission_id": response_id
    }

@app.get("/api/form-responses/{form_id}")
async def get_form_responses(form_id: str):
    """Get all saved responses for a form"""
    responses = load_form_responses(form_id)
    return {
        "form_id": form_id,
        "responses": responses,
        "total": len(responses)
    }

@app.get("/api/lookup-cedula/{cedula}")
async def lookup_cedula(cedula: str):
    """Look up respondent data by cedula from datos-generales form"""
    responses = load_form_responses("datos-generales")
    
    for response in responses:
        data = response.get("data", {})
        if data.get("numero_identificacion") == cedula:
            return {
                "found": True,
                "cedula": cedula,
                "nombre": data.get("nombre_completo"),
                "departamento": data.get("departamento_area"),
                "cargo": data.get("nombre_cargo"),
                "tipo_cargo": data.get("tipo_cargo")
            }
    
    return {
        "found": False,
        "cedula": cedula,
        "nombre": None,
        "departamento": None,
        "cargo": None,
        "tipo_cargo": None
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

@app.get("/api/export/excel/{questionnaire_id}")
async def export_excel(questionnaire_id: str):
    """Export questionnaire responses to Excel file"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        raise HTTPException(status_code=500, detail="openpyxl not installed")
    
    # Load questionnaire and responses
    questionnaire = load_questionnaire(questionnaire_id)
    responses = load_responses(questionnaire_id)
    
    if not responses:
        raise HTTPException(status_code=404, detail="No responses found")
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Respuestas"
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Build headers
    questions = questionnaire.get("questions", [])
    headers = ["ID", "Fecha", "Cédula", "Nombre", "Departamento"]
    for q in questions:
        headers.append(f"P{q['id']}: {q['text'][:50]}...")
    
    # Write headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Write data
    for row_idx, response in enumerate(responses, 2):
        # Build response dict for quick lookup
        response_dict = {r["question_id"]: r["response_value"] for r in response.get("responses", [])}
        
        # Basic info
        ws.cell(row=row_idx, column=1, value=response.get("id", "")[:8])
        ws.cell(row=row_idx, column=2, value=response.get("submitted_at", "")[:10])
        ws.cell(row=row_idx, column=3, value=response.get("respondent_cedula", ""))
        ws.cell(row=row_idx, column=4, value=response.get("respondent_name", ""))
        ws.cell(row=row_idx, column=5, value=response.get("department", ""))
        
        # Question responses
        for col_idx, q in enumerate(questions, 6):
            value = response_dict.get(q["id"], "")
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 25
    ws.column_dimensions['E'].width = 20
    
    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    filename = f"respuestas_{questionnaire_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/auth-config")
async def get_auth_config():
    """Get authentication configuration"""
    return {
        "allowed_user_id": os.getenv("ALLOWED_USER_ID")
    }

# --- SESSION ENDPOINTS ---

@app.get("/api/session/{cedula}")
async def get_session(cedula: str):
    """Get session status for a user"""
    sessions = load_sessions()
    session = sessions.get(cedula)
    
    if session:
        # Calculate progress
        completed_count = len(session.get("completed_forms", []))
        total_forms = len(SEQUENCE)
        progress = int((completed_count / total_forms) * 100)
        
        return {
            "found": True,
            "cedula": session["cedula"],
            "name": session.get("name"),
            "completed_forms": session.get("completed_forms", []),
            "current_step": session.get("current_step"),
            "progress": progress,
            "finished": session.get("current_step") == "completed"
        }
    
    return {"found": False}


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

@app.get("/ficha-datos")
async def serve_ficha_datos():
    """Serve the ficha de datos generales page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "ficha-datos.html"))

@app.get("/resultados-dashboard")
async def serve_results_dashboard():
    """Serve the results dashboard page"""
    return FileResponse(os.path.join(FRONTEND_DIR, "resultados-dashboard.html"))

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
    print("Sistema de Cuestionarios iniciado!")
    print("="*60)
    print("\n SELECTOR DE CUESTIONARIOS:")
    print("   http://localhost:8000/")
    print("\n ENCUESTA (ejemplo):")
    print("   http://localhost:8000/encuesta/estres")
    print("\n RESULTADOS (ejemplo):")
    print("   http://localhost:8000/resultados/estres")
    print(" IMPORTANTE: No cerrar esta ventana mientras se usen los cuestionarios")
    print("\n Agrega nuevos cuestionarios en:")
    print(f"   {QUESTIONNAIRES_DIR}")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

    print("="*60 + "\n")


