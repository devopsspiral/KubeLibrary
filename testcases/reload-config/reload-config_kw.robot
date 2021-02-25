*** Settings ***
Library           KubeLibrary
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py


*** Variables ***
${KUBE_CONFIG1}         %{KUBE_CONFIG1=./cluster1-conf}
${KUBE_CONFIG2}         %{KUBE_CONFIG2=./cluster2-conf}


*** Keywords ***
Connected to cluster-1 
    Reload Config  kube_config=${KUBE_CONFIG1}  incluster=False  cert_validation=False
    K8s Api Ping

Cluster has namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  Get Namespaces
    Should Contain    ${namespaces_list}    ${namespace}

Connected to cluster-2 
    Reload Config  kube_config=${KUBE_CONFIG2}  incluster=False  cert_validation=False
    K8s Api Ping

Connected to cluster-1 using bearer token 
    Reload Config    api_url=%{K8S_API_URL}    bearer_token=%{K8S_TOKEN}    ca_cert=%{K8S_CA_CRT}
    K8s Api Ping

Cluster has no namespace
    [Arguments]  ${namespace}
    @{namespaces_list}=  Get Namespaces
    Should Not Contain    ${namespaces_list}    ${namespace}

