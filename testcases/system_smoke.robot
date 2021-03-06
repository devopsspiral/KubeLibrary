*** Settings ***
Resource          ./system_smoke_kw.robot

*** Variables ***
${KUBELET_VERSION}     v1.20.0+k3s2
${NUM_NODES}           1
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
    When getting all pods names in "kube-system"
    Then all pods in "kube-system" are running or succeeded

Traefik has enough replicas
    [Documentation]  Test if Ingress (Traefik) has enough replicas
    [Tags]    cluster    smoke
    Given kubernetes API responds
    When getting all pods names in "kube-system"
    Then "traefik*" has "${NUM_WORKERS}" replicas

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
    [Tags]    grafana
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
