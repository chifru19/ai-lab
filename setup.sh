#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="ai-lab"
NAMESPACE="security-edge"

echo "==> Cleaning stale kind cluster context..."
kind delete cluster --name "$CLUSTER_NAME" 2>/dev/null || true

echo "==> Creating kind cluster..."
cat <<KIND_EOF | kind create cluster --name "$CLUSTER_NAME" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 8000
    hostPort: 8000
    protocol: TCP
KIND_EOF

echo "==> Ensuring namespace $NAMESPACE exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

echo "==> Applying Kubernetes manifests..."
kubectl apply -f deploy/

echo "==> Waiting for DaemonSet rollout readiness..."
kubectl rollout status daemonset/edge-ai-soar-triage -n "$NAMESPACE" --timeout=180s

POD_NAME=""
for i in {1..30}; do
  POD_NAME=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
  if [[ -n "${POD_NAME:-}" ]]; then
    break
  fi
  sleep 1
done

echo "==> Target pod: $POD_NAME"
echo "==> Pulling phi3:latest via port-forward..."
kubectl port-forward -n "$NAMESPACE" "$POD_NAME" 11434:11434 &
PF_PID=$!
sleep 3
curl -s -X POST http://localhost:11434/api/pull -d '{"name": "phi3:latest"}' || true
kill $PF_PID 2>/dev/null || true

echo "==> Testing triage endpoint..."
curl -i -X POST http://localhost:8000/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"log_line": "Failed password for invalid user admin from 10.0.0.99 port 50000 ssh2"}'
echo ""
