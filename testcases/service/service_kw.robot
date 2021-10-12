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
    @{namespace_services}=  Get Services In Namespace    ${namespace}  ${label}
    FOR  ${service}  IN  @{namespace_services}
        ${sevice_details}=  Get Service Details In Namespace  ${service}  ${namespace}
        ${label_key}=  Fetch From Left    ${label}    =
        ${label_value}=  Fetch From Right    ${label}    =
        Dictionary Should Contain Item    ${sevice_details.metadata.labels}    ${label_key}  ${label_value}
        ...  msg=Expected labels do not match.
    END

List all services in all namespaces
    @{services}=  Get Service For All Namespaces
    Log  \nservices in all namespaces:  console=True
    FOR  ${service}  IN  @{services}
        Log  ${service}  console=True
    END	
