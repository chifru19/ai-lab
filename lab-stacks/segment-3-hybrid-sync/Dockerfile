FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx

COPY lab-stacks/segment-3-hybrid-sync/ /app/
COPY lab-stacks/segment-4-edge-hpc/4gate-soar/gates/ /app/gates/

EXPOSE 8000
CMD ["uvicorn", "triage_daemon:app", "--host", "0.0.0.0", "--port", "8000"]
