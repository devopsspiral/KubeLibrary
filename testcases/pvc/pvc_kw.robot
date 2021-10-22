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
List pvcs by label
    [Arguments]  ${namespace}  ${label}
    @{namespace_pvcs}=  Get PVC In Namespace    ${namespace}  ${label}
    Log  List of PVCs in Namespace ${namespace} with Label ${label}: @{namespace_pvcs}  console=True
