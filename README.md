# KubeLibrary
[![CircleCI Build Status](https://circleci.com/gh/devopsspiral/KubeLibrary.svg?style=shield)](https://circleci.com/gh/devopsspiral/KubeLibrary)[![PyPI](https://img.shields.io/pypi/v/robotframework-kubelibrary)](https://pypi.org/project/robotframework-kubelibrary/)[![PyPi downloads](https://img.shields.io/pypi/dm/robotframework-kubelibrary.svg)](https://pypi.python.org/pypi/robotframework-kubelibrary)[![GitHub License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://raw.githubusercontent.com/devopsspiral/k3d-orb/master/LICENSE)[![Slack](https://img.shields.io/badge/slack-robotframework%2F%23kubernetes-blue)](https://robotframework.slack.com/archives/C017AKKS06R)


RobotFramework library for testing Kubernetes cluster

## Quick start

```
# install library itself
pip install robotframework-kubelibrary

# export KUBECONFIG
export KUBECONFIG=~/.kube/config

# run example tests
pip install robotframework-requests
git clone https://github.com/devopsspiral/KubeLibrary.git
cd KubeLibrary
robot -e prerelease testcases
```

## Example testcase

```
Pods in kube-system are ok
    [Documentation]  Test if all pods in kube-system initiated correctly and are running or succeeded
    [Tags]    cluster    smoke
    Given kubernetes API responds
    When getting all pods in  "kube-system"
    Then all pods in "kube-system" are running or succeeded

Grafana has correct version
    [Documentation]  Test if Grafana container image is in correct version
    [Tags]    grafana
    Given kubernetes API responds
    When accessing "grafana-" excluding "svclb" container images version in "default"
    Then "grafana/grafana:6.5.0" version is used

```

More examples in testcases/ directory.

To see all the tests passing execute below commands.

## Documentation

[Library docs](http://devopsspiral.com/KubeLibrary/)


### Cluster Tests
```
# run cluster tests
robot -i cluster -e prerelease testcases/
```

### Grafana Tests
```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana -f testcases/grafana/values.yaml

# run grafana tests
export KLIB_POD_PATTERN='grafana.*'
export KLIB_POD_ANNOTATIONS='{"kubelibrary":"testing"}'
export KLIB_POD_NAMESPACE=default

robot -i grafana -e prerelease testcases/
```
### Other Tests
These tests require the kubelib-test helm-chart to be installed in your test cluster.
```
# run other library tests
export KLIB_POD_PATTERN='busybox.*'
export KLIB_POD_NAMESPACE=kubelib-tests
export KLIB_POD_LABELS='job-name=busybox-job'

kubectl create namespace $KLIB_POD_NAMESPACE
kubectl label namespaces kubelib-tests test=test
helm install kubelib-test ./test-objects-chart -n $KLIB_POD_NAMESPACE

robot -i other -e prerelease testcases/
```
### Multi Cluster Tests
These tests require more than one cluster and utilize [KinD](https://kind.sigs.k8s.io/) as a setup.
[Download KinD and install it.](https://kind.sigs.k8s.io/docs/user/quick-start/)
```
# Create Test Cluster 1
kind create cluster --kubeconfig ./cluster1-conf --name kind-cluster-1

# Create namespace in Test Cluster 1
kubectl create namespace test-ns-1 --context kind-kind-cluster-1 --kubeconfig ./cluster1-conf
# For bearer token auth
kubectl apply -f testcases/reload-config/sa.yaml
MYSA_TOKEN_SECRET=$(kubectl get sa mysa -o jsonpath="{.secrets[0].name}")
export K8S_TOKEN=$(kubectl get secret $MYSA_TOKEN_SECRET --template={{.data.token}} | base64 -d)
kubectl get secret $MYSA_TOKEN_SECRET -o jsonpath="{.data.ca\.crt}" | base64 -d > ca.crt
export K8S_API_URL=$(kubectl config view -o jsonpath='{.clusters[0].cluster.server}')
export K8S_CA_CRT=./ca.crt

# Create Test Cluster 2
kind create cluster --kubeconfig ./cluster2-conf --name kind-cluster-2

# Create namespace in Test Cluster 2
kubectl create namespace test-ns-2 --context kind-kind-cluster-2 --kubeconfig ./cluster2-conf

robot -i reload-config -e prerelease testcases/

# Clean up
kind delete cluster --name kind-cluster-1
kind delete cluster --name kind-cluster-2
```

## Keywords documentation

Keywords documentation can be found in docs/.

## Further reading

[DevOps spiral article on KubeLibrary](https://devopsspiral.com/articles/k8s/robotframework-kubelibrary/)

[KubeLibrary: Testing Kubernetes with RobotFramework  | Humanitec](https://humanitec.com/blog/kubelibrary-testing-kubernetes-with-robotframework)

[RobotFramework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)

## Development

```
# clone repo
git clone https://github.com/devopsspiral/KubeLibrary.git
cd KubeLibrary

# create virtualenv
virtualenv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

Create keyword and test file, import KubeLibrary using below to point to library under development.

```
*** Settings ***

Library    ../src/KubeLibrary/KubeLibrary.py
```

For development cluster you can use k3s/k3d as described in [DevOps spiral article on K3d and skaffold](https://devopsspiral.com/articles/k8s/k3d-skaffold/).

### Generate docs

```
(
    # To generate keyword documentation a connection
    # to a cluster is not necessary. Skip to load a
    # cluster configuration.
    #
    # Set the variable local for the libdoc call only
    export INIT_FOR_LIBDOC_ONLY=1
    python -m robot.libdoc src/KubeLibrary docs/index.html
)
```
