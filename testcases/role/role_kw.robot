*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all roles in namespace
    [Arguments]  ${namespace}
    @{namespace_roles}=  Get Roles In Namespace    ${namespace}
    Length Should Be  ${namespace_roles}  2
    Log  \nRoles in namespace ${namespace_roles}:  console=True
    
List all role bindings in namespace
    [Arguments]  ${namespace}
    @{namespace_role_bindings}=  Get Role Bindings In Namespace    ${namespace}
    Length Should Be  ${namespace_role_bindings}  1
    Log  \nRole_binding in namespace ${namespace_role_bindings}:  console=True
