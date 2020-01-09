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
    When getting pods in "kube-system"
    Then all pods in "kube-system" are running or succeeded

Grafana has correct version
    [Documentation]  Test if Grafana container image is in correct version
    [Tags]    grafana
    Given kubernetes API responds
    When accessing "grafana-" excluding "svclb" container images version in "default"
    Then "grafana/grafana:6.5.0" version is used

```

More examples in testcases/ directory.

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

For development cluster you can use k3s/k3d as described in [DevOps spiral article on K3d and skaffold](https://devopsspiral.com/articles/k8s/k3d-skaffold/). To see all the tests passing you can also install Grafana using

```
helm install grafana stable/grafana -f testcases/grafana/values.yaml
```

Generate docs

```
python -m robot.libdoc src/KubeLibrary/KubeLibrary.py docs/KubeLibrary.html
```