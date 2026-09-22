#!/usr/bin/env bash
set -euo pipefail

echo "==> Cleaning stale kind cluster..."
kind delete cluster --name ai-lab 2>/dev/null || true

echo "==> Creating fresh kind cluster..."
kind create cluster --name ai-lab --config - <<KIND
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 8000
    hostPort: 8000
    protocol: TCP
KIND

kubectl config use-context kind-ai-lab

echo "==> Ensuring namespace security-edge exists..."
kubectl create namespace security-edge --dry-run=client -o yaml | kubectl apply -f -

echo "==> Applying Kubernetes manifests from deploy/..."
kubectl apply -f deploy/

echo "==> Waiting for DaemonSet rollout readiness..."
kubectl rollout status daemonset/edge-ai-soar-triage -n security-edge --timeout=180s

echo "==> Waiting for pod scheduling index..."
POD_NAME=""
for i in {1..30}; do
  POD_NAME=$(kubectl get pods -n security-edge -o jsonpath="{.items[0].metadata.name}" 2>/dev/null || true)
  if [[ -n "${POD_NAME:-}" ]]; then
    break
  fi
  sleep 1
done

echo "==> Target pod: $POD_NAME"

CONTAINER_NAME=$(kubectl get pod -n security-edge "$POD_NAME" -o jsonpath="{.spec.containers[*].name}" | tr " " "
" | grep -iE "ollama|sidecar" | head -n1 || true)
if [[ -z "${CONTAINER_NAME:-}" ]]; then
  CONTAINER_NAME="ollama-sidecar"
fi
echo "==> Target container: $CONTAINER_NAME"

echo "==> Pulling model phi3:latest in $CONTAINER_NAME..."
kubectl exec -n security-edge "$POD_NAME" -c "$CONTAINER_NAME" -- ollama pull phi3:latest || true

echo "==> Verifying model list..."
kubectl exec -n security-edge "$POD_NAME" -c "$CONTAINER_NAME" -- ollama list || true

echo "==> Testing triage endpoint..."
curl -i -X POST http://localhost:8000/v1/triage   -H "Content-Type: application/json"   -d '{"log_line": "Failed password for invalid user admin from 10.0.0.99 port 50000 ssh2"}'
echo ""
