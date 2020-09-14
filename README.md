# KubeLibrary

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
robot testcases
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

### Cluster Tests
```
# run cluster tests
robot -i cluster testcases/
```

### Grafana Tests
```
helm install grafana stable/grafana -f testcases/grafana/values.yaml

# run grafana tests
export KLIB_POD_PATTERN='grafana.*'
export KLIB_POD_ANNOTATIONS='{"checksum/config":"3bb97e1695589c9bcdf6a6cd10c03517286ab7697626e6f02dd6fb2bc4a27796"}'
export KLIB_POD_NAMESPACE=default

robot -i grafana testcases/
```

### Octopus Tests
```
git clone https://github.com/kyma-incubator/octopus
helm install octopus octopus/chart/octopus/

# run octopus tests
export KLIB_RESOURCE_LIMITS_MEMORY=30Mi
export KLIB_POD_PATTERN='octopus.*'
export KLIB_RESOURCE_REQUESTS_CPU=100m
export KLIB_POD_LABELS='{"app":"octopus"}'
export KLIB_RESOURCE_LIMITS_CPU=100m
export KLIB_ENV_VARS='{"SECRET_NAME":"webhook-server-secret"}'
export KLIB_POD_NAMESPACE=default
export KLIB_RESOURCE_REQUESTS_MEMORY=20Mi

robot -i octopus testcases/
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

robot -i other testcases/
```
### Multi Cluster Tests
These tests require more than one cluster and utilize [KinD](https://kind.sigs.k8s.io/) as a setup.
[Download KinD and install it.](https://kind.sigs.k8s.io/docs/user/quick-start/)
```
# Create Test Cluster 1
kind create cluster --kubeconfig ./cluster1-conf --name kind-cluster-1

# Create namespace in Test Cluster 1
kubectl create namespace test-ns-1 --context kind-kind-cluster-1 --kubeconfig ./cluster1-conf

# Create Test Cluster 2
kind create cluster --kubeconfig ./cluster2-conf --name kind-cluster-2

# Create namespace in Test Cluster 2
kubectl create namespace test-ns-2 --context kind-kind-cluster-2 --kubeconfig ./cluster2-conf

robot -i reload-config testcases/

# Clean up
kind delete cluster --name kind-cluster-1
kind delete cluster --name kind-cluster-2
```

## Keywords documentation

Keywords documentation can be found in docs/.

## Further reading

[DevOps spiral article on KubeLibrary](https://devopsspiral.com/articles/k8s/robotframework-kubelibrary/)

[RobotFramewrok User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)

## Development

```
# clone repo
git clone https://github.com/devopsspiral/KubeLibrary.git
cd KubeLibrary

# create virtualenv
virtualenv .venv
. .venv/bin/activate
pip install -r requirements
```

Create keyword and test file, import KubeLibrary using below to point to library under development.

| ***** Settings ***** |

| Library    ../src/KubeLibrary/KubeLibrary.py |

For development cluster you can use k3s/k3d as described in [DevOps spiral article on K3d and skaffold](https://devopsspiral.com/articles/k8s/k3d-skaffold/).

Generate docs

```
python -m robot.libdoc src/KubeLibrary/KubeLibrary.py docs/KubeLibrary.html
```