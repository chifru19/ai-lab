import httpx
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

async def evaluate(log_line: str) -> dict:
    prompt = f"Analyze security severity (LOW/MEDIUM/HIGH/CRITICAL) for log: {log_line}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": "phi3:latest", "prompt": prompt, "stream": False}
            )
            data = resp.json()
            return {"raw_response": data.get("response", ""), "status": "success"}
    except Exception as e:
        return {"raw_response": f"fallback_error: {e}", "status": "error"}
