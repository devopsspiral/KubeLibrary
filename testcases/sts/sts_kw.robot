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
List sts by label
    [Arguments]  ${namespace}  ${label}
    @{namespace_sts}=  List namespaced stateful set    ${namespace}  ${label}
    @{namespace_sts_names}=    Filter Names    ${namespace_sts}
    Log  List of STSs in Namespace ${namespace} with Label ${label}: @{namespace_sts_names}  console=True

List sts by pattern
    [Arguments]  ${pattern}  ${namespace}
    @{namespace_sts}=  List namespaced stateful set by pattern    ${pattern}  ${namespace}
    @{namespace_sts_names}=    Filter Names    ${namespace_sts}
    Log  List of STSs in Namespace ${namespace} with Patter ${pattern}: @{namespace_sts_names}  console=True