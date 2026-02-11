import json
import random
import uuid
from datetime import datetime
import os

def generate_mock_data(num_responses=30):
    questionnaires = ["datos-generales", "estres", "extralaborales", "intralaborales-a"]
    
    for q_id in questionnaires:
        responses = []
        with open(f"backend/questionnaires/{q_id}.json", "r", encoding="utf-8") as f:
            q_data = json.load(f)
            
            if q_id == "datos-generales":
                # Handle form type questionnaire
                fields = []
                for section in q_data["sections"]:
                    fields.extend(section["fields"])
                
                for i in range(num_responses):
                    resp_id = str(uuid.uuid4())
                    cedula = str(random.randint(10000000, 99999999))
                    user_responses = []
                    for field in fields:
                        val = ""
                        if field["id"] == "ciudad_residencia":
                            val = random.choice(["Popayán", "Santander de Quilichao", "Puerto Tejada", "Cali", "Jamundí", "Guapi", "Timbío"])
                        elif field["type"] in ["radio", "select"]:
                            val = random.choice([o["value"] for o in field["options"]])
                        elif field["type"] == "number":
                            val = random.randint(field.get("min", 0), field.get("max", 2010))
                        else:
                            val = f"Test {field['id']}"
                        
                        user_responses.append({
                            "question_id": field["id"],
                            "response_value": val
                        })
                    responses.append({
                        "id": resp_id,
                        "submitted_at": datetime.now().isoformat(),
                        "respondent_cedula": cedula,
                        "responses": user_responses
                    })
            else:
                num_questions = len(q_data["questions"])
                options = [opt["value"] for opt in q_data["options"]]
                
                for i in range(num_responses):
                    resp_id = str(uuid.uuid4())
                    cedula = str(random.randint(10000000, 99999999))
                    user_responses = []
                    for q in q_data["questions"]:
                        val = random.choice(options)
                        user_responses.append({
                            "question_id": q["id"],
                            "response_value": val
                        })
                    responses.append({
                        "id": resp_id,
                        "submitted_at": datetime.now().isoformat(),
                        "respondent_cedula": cedula,
                        "responses": user_responses
                    })
            
        with open(f"backend/data/responses_{q_id}.json", "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)

    print(f"Generated {num_responses} mock responses for {questionnaires}")

if __name__ == "__main__":
    os.makedirs("backend/data", exist_ok=True)
    generate_mock_data()
