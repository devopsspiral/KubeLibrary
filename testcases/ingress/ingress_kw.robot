*** Settings ***
Library           Collections
Library           RequestsLibrary
Library           String
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List ingresses by label
    [Arguments]  ${namespace}  ${label}
    @{namespace_ingresses}=  Get Ingresses In Namespace    ${namespace}  ${label}
    Length Should Be  ${namespace_ingresses}  1
    FOR  ${ingress}  IN  @{namespace_ingresses}
        ${ingress_details}=  Get Ingress Details In Namespace  ${ingress}  ${namespace}
        ${label_key}=  Fetch From Left    ${label}    =
        ${label_value}=  Fetch From Right    ${label}    =
        Dictionary Should Contain Item    ${ingress_details.metadata.labels}    ${label_key}  ${label_value}
        ...  msg=Expected labels do not match.
        Log  Ingress Host Url: ${ingress_details.spec.rules[0].host}  console=True
    END

List all ingresses in namespace
    [Arguments]  ${namespace}
    @{namespace_ingresses}=  Get Ingresses In Namespace    ${namespace}
    Log  \nIngresses in namespace ${namespace}:  console=True
    Length Should Be  ${namespace_ingresses}  1
    FOR  ${ingress}  IN  @{namespace_ingresses}
        ${ingress_details}=  Get Ingress Details In Namespace  ${ingress}  ${namespace}
        Log  ${ingress_details.metadata.name}  console=True
        Set Global Variable    ${ingress_name}    ${ingress_details.metadata.name}
            Set Global Variable    ${ingress}    ${ingress_details}
    END

Edit obtained ingress
    [Arguments]     ${ingress_name}
    ${ingress.metadata.name}=  Set Variable  ${ingress_name}
    ${ingress.metadata.resource_version}=  Set Variable  ${None}
    Set Global Variable    ${new_ingress}    ${ingress}

Create new ingress in namespace
    [Arguments]  ${namespace}
    Log  \nCreate new ingress in namespace ${namespace}  console=True
    ${new_ing}=    Create Ingress In Namespace  ${namespace}  ${new_ingress}
    Log  ${new_ing}  console=True

Delete created ingress in namespace
    [Arguments]  ${ingress_name}    ${namespace}
    Log  \nDelete ingress in namespace ${namespace}  console=True
    Log  ${ingress_name}  console=True
    ${status}=    Delete Ingress In Namespace  ${ingress_name}    ${namespace}
    Log  ${status}
