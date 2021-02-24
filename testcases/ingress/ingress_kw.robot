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
