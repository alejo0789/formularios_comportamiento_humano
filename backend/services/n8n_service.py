import httpx
import os
import json
from typing import Dict, Any

class N8NService:
    def __init__(self):
        self.webhook_url = os.getenv("N8N_WEBHOOK_URL")

    async def trigger_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends data to n8n webhook for advanced processing (AI agent).
        """
        if not self.webhook_url:
            print("Warning: N8N_WEBHOOK_URL not configured")
            return {"status": "skipped", "message": "N8n not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error triggering n8n: {e}")
            return {"status": "error", "message": str(e)}
