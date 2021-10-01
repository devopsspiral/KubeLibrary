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
    Length Should Be  ${namespace_roles}  1
    Log  \nRoles in namespace ${namespace_roles}:  console=True
    FOR  ${role}  IN  @{namespace_roles}
        ${role_details}=  Get Role Details In Namespace  ${role}  ${namespace}
        Log  ${role_details.metadata.name}  console=True
        Set Global Variable    ${role_name}    ${role_details.metadata.name}
      	Set Global Variable    ${role}    ${role_details}
    END    

List all role bindings in namespace
    [Arguments]  ${namespace}
    @{namespace_role_bindings}=  Get Role Bindings In Namespace    ${namespace}
    Length Should Be  ${namespace_role_bindings}  1
    Log  \nRole_binding in namespace ${namespace_role_bindings}:  console=True
    
Edit obtained role
    [Arguments]     ${role_name}    
    ${role.metadata.name}=  Set Variable  ${role_name}     
    ${role.metadata.resource_version}=  Set Variable  ${None}    
    Set Global Variable    ${new_role}    ${role}

Create new role in namespace
    [Arguments]  ${namespace}
    Log  \nCreate new role in namespace ${namespace}  console=True    
    ${new_role}=    Create Role In Namespace  ${namespace}  ${new_role}    
    Log  ${new_role}  console=True

Delete created role in namespace
    [Arguments]  ${role_name}    ${namespace}    
    Log  \nDelete role in namespace ${namespace}  console=True    
    ${status}=    Delete Role In Namespace  ${role_name}    ${namespace}    
    Log  ${status}
