#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="security-edge"
POD_NAME=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=edge-ai-soar -o jsonpath='{.items[0].metadata.name}')

echo "==> Checking Ollama models in $POD_NAME..."
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c ollama-sidecar -- ollama list || true

echo "==> Pulling default model (adjust model name if needed, e.g., llama3 / phi3)..."
# Replace 'phi3' or 'llama3' with the exact model your app expects in env vars
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c ollama-sidecar -- ollama pull phi3

echo "==> Verifying model list..."
kubectl exec -n "$NAMESPACE" "$POD_NAME" -c ollama-sidecar -- ollama list
