#!/usr/bin/env bash
set -euo pipefail

export K8S_TOKEN_SECRET=mysa-token
export KUBE_CONFIG1=/.kube/testk3d-1
export KUBE_CONFIG2=/.kube/testk3d-2
export CLUSTER1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' k3d-testk3d-1-server-0)
export CLUSTER2_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' k3d-testk3d-2-server-0)
export HOME=/tmp
mkdir -p /tmp/.kube
export KUBE_CONFIG1_FILE=/tmp/kubeconfig-testk3d-1.yaml
export KUBE_CONFIG2_FILE=/tmp/kubeconfig-testk3d-2.yaml
export K8S_API_URL="https://$CLUSTER1_IP:6443"
export K8S_CA_CRT=/.kube/ca.crt

docker run --rm --volumes-from kubeconfig alpine:3.4 sh -c "cat $KUBE_CONFIG1" > "$KUBE_CONFIG1_FILE"
docker run --rm --volumes-from kubeconfig alpine:3.4 sh -c "cat $KUBE_CONFIG2" > "$KUBE_CONFIG2_FILE"

cat > /tmp/sa.yaml <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mysa
  labels:
    source: mysa
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: mysa-admin-binding
subjects:
- kind: ServiceAccount
  name: mysa
  namespace: default
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: Secret
metadata:
  name: mysa-token
  annotations:
    kubernetes.io/service-account.name: mysa
type: kubernetes.io/service-account-token
EOF

docker run --rm \
  --network container:k3d-testk3d-1-serverlb \
  --volumes-from kubeconfig \
  -v /tmp/sa.yaml:/tmp/sa.yaml \
  --entrypoint sh \
  bitnami/kubectl:latest -c "kubectl --kubeconfig=$KUBE_CONFIG1 create namespace test-ns-1 && kubectl --kubeconfig=$KUBE_CONFIG1 apply -f /tmp/sa.yaml"

export K8S_TOKEN=$(docker run --rm \
  --network container:k3d-testk3d-1-serverlb \
  --volumes-from kubeconfig \
  --entrypoint sh \
  bitnami/kubectl:latest -c "kubectl --kubeconfig=$KUBE_CONFIG1 get secret $K8S_TOKEN_SECRET --template='{{.data.token}}' | base64 --decode | tr -d '\r\n'")

docker run --rm \
  --network container:k3d-testk3d-1-serverlb \
  --volumes-from kubeconfig \
  --entrypoint sh \
  bitnami/kubectl:latest -c "kubectl --kubeconfig=$KUBE_CONFIG1 get secret $K8S_TOKEN_SECRET -o jsonpath='{.data.ca\\.crt}' | base64 --decode" > ca.crt

docker cp ca.crt kubeconfig:$K8S_CA_CRT

sed -i "s|server: https://127.0.0.1:6443|server: https://$CLUSTER1_IP:6443|g" "$KUBE_CONFIG1_FILE" || true
sed -i "s|server: https://127.0.0.1:6443|server: https://$CLUSTER2_IP:6443|g" "$KUBE_CONFIG2_FILE" || true

docker cp "$KUBE_CONFIG1_FILE" kubeconfig:$KUBE_CONFIG1
docker cp "$KUBE_CONFIG2_FILE" kubeconfig:$KUBE_CONFIG2
docker cp ca.crt kubeconfig:$K8S_CA_CRT

for f in "$KUBE_CONFIG1_FILE" "$KUBE_CONFIG2_FILE"; do
  if [ ! -f "$f" ]; then
    echo "kubeconfig $f not present, skipping" >&2
    continue
  fi
  user_name=$(HOME=/tmp command kubectl --kubeconfig="$f" config view -o jsonpath='{.users[0].name}' 2>/dev/null || true)
  if [ -n "$user_name" ]; then
    HOME=/tmp command kubectl --kubeconfig="$f" config set-credentials "$user_name" --token="$K8S_TOKEN" || true
  else
    echo "Could not determine user name from $f" >&2
  fi
done

docker cp "$KUBE_CONFIG1_FILE" kubeconfig:$KUBE_CONFIG1 || true
docker cp "$KUBE_CONFIG2_FILE" kubeconfig:$KUBE_CONFIG2 || true

docker create --rm -it \
  --network k3d-testk3d-1 \
  --volumes-from kubeconfig \
  -e KUBE_CONFIG1=$KUBE_CONFIG1 \
  -e KUBE_CONFIG2=$KUBE_CONFIG2 \
  -e K8S_API_URL=$K8S_API_URL \
  -e K8S_TOKEN=$K8S_TOKEN \
  -e K8S_CA_CRT=$K8S_CA_CRT \
  --name kubelibrary kubelibrary -i reload-config /testcases/
docker network connect k3d-testk3d-2 kubelibrary
docker start -a kubelibrary