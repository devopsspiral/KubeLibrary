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
List services by label
    [Arguments]  ${namespace}  ${label}
    @{namespace_services}=  List Namespaced Service    ${namespace}  ${label}
    Log  \nServices in namespace ${namespace}:  console=True
    FOR  ${service}  IN  @{namespace_services}
        Log  ${service.metadata.name}  console=True
        ${sevice_details}=  Read Namespaced Service  ${service}  ${namespace}
        ${label_key}=  Fetch From Left    ${label}    =
        ${label_value}=  Fetch From Right    ${label}    =
        Dictionary Should Contain Item    ${sevice_details.metadata.labels}    ${label_key}  ${label_value}
        ...  msg=Expected labels do not match.
    END


