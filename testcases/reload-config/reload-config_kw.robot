*** Settings ***

*** Keywords ***
Connected to cluster-1 
    Import Library  ${CURDIR}/../../src/KubeLibrary/KubeLibrary.py    kube_config=./cluster1-conf
    K8s Api Ping

Cluster has namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  List Namespaces
    Should Contain    ${namespaces_list}    ${namespace}

Connected to cluster-2 
    Reload Config  kube_config=./cluster2-conf
    K8s Api Ping

Cluster has no namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  List Namespaces
    Should Not Contain    ${namespaces_list}    ${namespace}

