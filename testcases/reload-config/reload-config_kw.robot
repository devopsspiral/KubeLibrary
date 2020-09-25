*** Settings ***

*** Variables ***
${KUBE_CONFIG1}         %{KUBE_CONFIG1=./cluster1-conf}
${KUBE_CONFIG2}         %{KUBE_CONFIG2=./cluster2-conf}


*** Keywords ***
Connected to cluster-1 
    Import Library  KubeLibrary  kube_config=${KUBE_CONFIG1}  incluster=False  cert_validation=False
    K8s Api Ping

Cluster has namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  Get Namespaces
    Should Contain    ${namespaces_list}    ${namespace}

Connected to cluster-2 
    Reload Config  kube_config=${KUBE_CONFIG2}  incluster=False  cert_validation=False
    K8s Api Ping

Cluster has no namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  Get Namespaces
    Should Not Contain    ${namespaces_list}    ${namespace}

