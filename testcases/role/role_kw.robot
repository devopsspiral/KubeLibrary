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
    @{namespace_roles}=  Get Role In Namespace    ${namespace}
    Length Should Be  ${namespace_roles}  1
    Log  \nRoles in namespace ${namespace_roles}:  console=True
    
List all role bindings in namespace
    [Arguments]  ${namespace}
    @{namespace_role_binding}=  Get Role Binding In Namespace    ${namespace}
    Length Should Be  ${namespace_role_binding}  1
    Log  \nRole_binding in namespace ${namespace_role_binding}:  console=True
