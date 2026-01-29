from typing import List, Dict, Any, Optional

class TemplateService:
    def __init__(self):
        # In a real app, these would load from JSON files or DB
        self.templates = {
            "questionnaire": [
                {
                    "id": "std_questionnaire",
                    "name": "Cuestionario Estándar",
                    "description": "Formulario clásico de preguntas y opción múltiple",
                    "icon": "📝",
                    "category": "form"
                },
                {
                    "id": "conversational_bot",
                    "name": "Chatbot Conversacional",
                    "description": "Convierte el cuestionario en una conversación fluida",
                    "icon": "💬",
                    "category": "conversation"
                }
            ],
            "form": [
                {
                    "id": "modern_form",
                    "name": "Formulario Moderno",
                    "description": "Diseño limpio con validaciones en tiempo real",
                    "icon": "📋",
                    "category": "form"
                }
            ],
            "emoji": [
                {
                    "id": "emoji_feedback",
                    "name": "Feedback con Emojis",
                    "description": "Escalas de valoración visuales usando emojis",
                    "icon": "😀",
                    "category": "visual"
                }
            ]
        }

    def get_suggestions(self, pdf_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggests templates based on the analysis of the PDF and pre-fills them with extracted data.
        """
        doc_type = pdf_analysis.get("document_type", "unknown")
        extracted_questions = pdf_analysis.get("questions", [])
        title = pdf_analysis.get("title", "Nuevo Formulario")
        
        suggestions = []

        def create_base_form(template_id, name, description, category, icon):
            return {
                "id": template_id,
                "name": name,
                "description": description,
                "category": category,
                "icon": icon,
                "preview_config": {
                    "title": title,
                    "description": "Generado desde PDF",
                    "questions": [
                        {
                            "id": i + 1,
                            "text": q,
                            "type": "text" if category == "form" else "single_choice",
                            "options": [{"value": 1, "label": "Sí"}, {"value": 0, "label": "No"}] if category != "form" else []
                        }
                        for i, q in enumerate(extracted_questions)
                    ]
                }
            }

        suggestions.append(create_base_form("standard_form", "Formulario Estándar", "Formulario digital clásico", "form", "📋"))

        if doc_type == "questionnaire" or len(extracted_questions) > 0:
            suggestions.append(create_base_form("conversational_bot", "Chatbot Conversacional", "Formato chat interactivo", "conversation", "💬"))

        if doc_type == "questionnaire":
             suggestions.append(create_base_form("emoji_feedback", "Encuesta Visual", "Escalas con emojis", "visual", "😀"))
        
        return suggestions

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Return all available templates"""
        all_templates = []
        for category in self.templates.values():
            all_templates.extend(category)
        return all_templates
