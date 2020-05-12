*** Settings ***
Library            JSONLibrary
Resource          ./system_smoke_kw.robot

*** Variables ***
${KUBELET_VERSION}     v1.16.2-k3s.1
${NUM_NODES}           2
${NUM_WORKERS}         1

*** Test Cases ***
Kubernetes has correct version
    [Documentation]  Test if Kubernetes has correct version
    [Tags]    cluster    smoke
    Given kubernetes has "${NUM_NODES}" healthy nodes
    When getting kubelet version
    Then Kubernetes version is correct

Pods in kube-system are ok
    [Documentation]  Test if all pods in kube-system initiated correctly and are running or succeeded
    [Tags]    cluster    smoke
    Given kubernetes API responds
    When getting pods in "kube-system"
    Then all pods in "kube-system" are running or succeeded

Traefik has enough replicas
    [Documentation]  Test if Ingress (Traefik) has enough replicas
    [Tags]    cluster    smoke
    Given kubernetes API responds
    When getting pods in "kube-system"
    Then "traefik*" has "${NUM_WORKERS}" replicas

Grafana has correct version
    [Documentation]  Test if Grafana container image is in correct version
    [Tags]    grafana
    Given kubernetes API responds
    When accessing "grafana-" excluding "svclb" container images version in "default"
    Then "grafana/grafana:6.5.0" version is used

Grafana is persistent
    [Documentation]  Test if Grafana is deployed with persistent storage
    [Tags]    grafana
    Given kubernetes API responds
    When getting pvcs in "default"
    Then "grafana" has "1" pvcs

Grafana has 1GB storage
    [Documentation]  Test if Grafana has 1GB storage
    [Tags]    grafana
    Given kubernetes API responds
    When getting pvc size for "grafana" in "default"
    Then pvc size is "1Gi"

Grafana service points to pods
    [Documentation]  Test if Grafana service selectors points to pods
    Given kubernetes API responds
    When getting "grafana" endpoint in "default"
    Then endpoint points to "grafana*" pod

Grafana service is correctly exposed
    [Documentation]  Test if Grafana service is correctly exposed
    [Tags]    grafana
    Given kubernetes API responds
    When getting service "grafana" details in "default"
    Then service is exposed on "3000" port
    And service has "LoadBalancer" type
    And service has LB ip assigned

Grafana is responding
    [Documentation]  Test if Grafana service ip is accessible
    [Tags]    grafana
    Given "grafana" service ip and port in "default" is known
    When session is created
    Then service is responding on path "/"
Namespace Create
   [Tags]  cluster
   ${namespace_obj}=  Load JSON From File  ./namespace_test.json
   ${response}  NAMESPACE CREATE  ${namespace_obj}
   Sleep  5s
Create Pod
    [Tags]  cluster
    ${pod_object}=  Load JSON From File  ./pod_test.json
    CREATE POD IN NAMESPACE  ${pod_object}  robot-demo
    Sleep  5s

Create Service
    [Tags]  cluster
    ${service_object}=  Load JSON From File  ./service.json
    CREATE SERVICE IN NAMESPACE  ${service_object}  robot-demo
    Sleep  5s

Delete Service
    [Tags]  cluster
    DELETE SERVICE IN NAMESPACE  robot-service  robot-demo

Delete Pod
    [Tags]  cluster
    ${response}=  DELETE POD IN NAMESPACE  robot-test-validation  robot-demo

Namespace Delete
    [Tags]  cluster
    ${Response}=  NAMESPACE DELETE  robot-demo

Fetch Deployment in namespace
    [Tags]  deployment
    ${Response}=  GET DEPLOYMENTS IN NAMESPACE  test
    Log to Console  ${Response}
Fetch Daemonset in namespace
    [Tags]  deployment
    ${Response}=  GET DAEMONSETS IN NAMESPACE  test
    Log to Console  ${Response}
    
