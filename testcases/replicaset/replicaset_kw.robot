*** Settings ***
Library           Collections
Library           RequestsLibrary
# For regular execution
#Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/config

*** Keywords ***
List all replicasets in namespace
    [Arguments]  ${namespace}  ${label}=${EMPTY}
    @{namespace_replicasets}=  Get Replicasets In Namespace    .*  ${namespace}  ${label}
    Log To Console  \nReplicasets in namespace ${namespace}:  console=True
    FOR  ${replicaset}  IN  @{namespace_replicasets}
        Log To Console   ${replicaset.metadata.name}  console=True
    END

