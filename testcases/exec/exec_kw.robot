*** Settings ***
# For regular execution
Library    KubeLibrary
# For incluster execution
#Library    KubeLibrary    None    True    False
# For development
#Library    ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Variables ***
${namespace}    default

*** Keywords ***
Set Pod Name For namespace
    ${namespace_pods}    List Namespaced POD By Pattern    .*    ${namespace}
    ${namespace_pods_names}    Filter Names    ${namespace_pods}
    Set Test Variable    ${POD_NAME}    ${namespace_pods_names}[0]
    ${pod}    read_namespaced_pod_status    ${POD_NAME}
    Log To Console    ${pod}
