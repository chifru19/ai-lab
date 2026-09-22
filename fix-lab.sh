#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="security-edge"
POD_NAME=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')
CONTAINERS=$(kubectl get pod -n "$NAMESPACE" "$POD_NAME" -o jsonpath='{.spec.containers[*].name}')
echo "==> Target Pod: $POD_NAME"
echo "==> Available Containers: $CONTAINERS"

OLLAMA_CONTAINER=""
for c in $CONTAINERS; do
  if [[ "$c" =~ ollama|sidecar|llm ]]; then
    OLLAMA_CONTAINER="$c"
    break
  fi
done
if [[ -z "$OLLAMA_CONTAINER" ]]; then
  OLLAMA_CONTAINER=$(echo "$CONTAINERS" | awk '{print $1}')
fi
echo "==> Selected Container: $OLLAMA_CONTAINER"

echo "==> Inspecting Ollama API tags first..."
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c "$OLLAMA_CONTAINER" -- curl -s http://localhost:11434/api/tags || true

echo "==> Pulling phi3:latest via Ollama REST API..."
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c "$OLLAMA_CONTAINER" -- curl -s -X POST http://localhost:11434/api/pull -d '{"name": "phi3:latest"}'

echo "==> Re-verifying model tags..."
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c "$OLLAMA_CONTAINER" -- curl -s http://localhost:11434/api/tags

echo "==> Retesting triage endpoint..."
curl -i -X POST http://localhost:8000/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"log_line": "Failed password for invalid user admin from 10.0.0.99 port 50000 ssh2"}'
echo ""
