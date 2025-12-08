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
List all statefulsets in namespace
    [Arguments]  ${namespace}  ${label}=${EMPTY}
    @{namespace_statefulsets}=  list_namespaced_stateful_set_by_pattern    .*  ${namespace}  ${label}
    Log To Console  \nStatefulsets in namespace ${namespace}:  console=True
    FOR  ${statefulset}  IN  @{namespace_statefulsets}
        Log To Console   ${statefulset.metadata.name}  console=True
    END

