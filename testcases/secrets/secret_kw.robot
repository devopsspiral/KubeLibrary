*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all secrets in namespace
    [Arguments]  ${namespace}  ${label}=${EMPTY}
    @{namespace_secrets}=  List Namespaced Secret By Pattern    .*  ${namespace}  ${label}
    Log  \nSecrets in namespace ${namespace}:  console=True
    FOR  ${secret}  IN  @{namespace_secrets}
        Log  ${secret.metadata.name}  console=True
    END

Read grafana secrets
    @{namespace_secrets}=  List Namespaced Secret By Pattern    ^grafana$  default
    Length Should Be  ${namespace_secrets}  1
  
    Set Suite Variable  ${GRAFANA_USER}  ${namespace_secrets[0].data["admin-user"]}
    ${GRAFANA_USER}=  Evaluate  base64.b64decode($GRAFANA_USER)  modules=base64
    Log  Grafana user: ${GRAFANA_USER}  console=True
    
    Set Suite Variable  ${GRAFANA_PASSWORD}  ${namespace_secrets[0].data["admin-password"]}
    ${GRAFANA_PASSWORD}=  Evaluate  base64.b64decode($GRAFANA_PASSWORD)  modules=base64
    Log  Grafana password: ${GRAFANA_PASSWORD}  console=True
