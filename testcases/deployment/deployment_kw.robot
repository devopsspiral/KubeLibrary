*** Settings ***
Library           Collections
Library           RequestsLibrary
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all deployments in namespace
    [Arguments]  ${namespace}  ${label}=${EMPTY}
    @{namespace_deployments}=  Get Deployments In Namespace    .*  ${namespace}  ${label}
    Log  \nDeployments in namespace ${namespace}:  console=True
    FOR  ${deployment}  IN  @{namespace_deployments}
        Log  ${deployment.metadata.name}  console=True
    END

Show Grafana Deployment
    @{namespace_deployments}=  Get Deployments In Namespace    grafana  default
    FOR  ${deployment}  IN  @{namespace_deployments}
        Should be Equal   ${deployment.metadata.name}  grafana
        Set Global Variable  ${DEPLOYMENT}  ${deployment}
        Log  \nDeployment ${deployment.metadata.name}:  console=True
        Log  ${deployment}  console=True
        Log  \n  console=True
    END

Assert Replica Status
    Should be Equal  ${DEPLOYMENT.status.available_replicas}  ${DEPLOYMENT.status.replicas}
    ...  msg=Available replica count (${DEPLOYMENT.status.available_replicas}) doesn't match current replica count (${DEPLOYMENT.status.replicas})




