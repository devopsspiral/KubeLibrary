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
List all service accounts for matching name pattern in namespace
    [Arguments]  ${name_pattern}    ${namespace}
    @{namespace_service_account}=  Get Service Accounts In Namespace    ${name_pattern}  ${namespace}
    Log  \nService Accounts in namespace ${namespace}:  console=True
    FOR  ${sa}  IN  @{namespace_service_account}
        Log  ${sa.metadata.name}  console=True
        Set Global Variable    ${sa_name}    ${sa.metadata.name}
        Set Global Variable    ${service_account}    ${sa}
    END

List all service accounts for matching name pattern in namespace with label
    [Arguments]  ${name_pattern}  ${namespace}  ${label}
    @{namespace_service_account}=  Get Service Accounts In Namespace    ${name_pattern}  ${namespace}  ${label}
    Log  \nService Accounts in namespace ${namespace}:  console=True
    FOR  ${sa}  IN  @{namespace_service_account}
        Log  ${sa.metadata.name}  console=True
        Dictionary Should Contain Item    ${sa.metadata.labels}    TestLabel    mytestlabel
        ...  msg=Expected labels do not match.
    END

Edit obtained service account
    [Arguments]     ${service_account_name}
    ${service_account.metadata.name}=  Set Variable  ${service_account_name}
    ${service_account.metadata.resource_version}=  Set Variable  ${None}
    Set Global Variable    ${new_service_account}    ${service_account}

Create new service account in namespace
    [Arguments]  ${namespace}
    ${new_sa}=    Create Service Account In Namespace  ${namespace}  ${new_service_account}
    Log  ${new_sa}

Delete created service account in namespace
    [Arguments]  ${service_account_name}    ${namespace}
    ${status}=    Delete Service Account In Namespace  ${service_account_name}    ${namespace}
    Log  ${status}

List all service_accounts in all namespaces
    @{service_accounts}=  Get service_account For All Namespaces
    Log  \nservice_accounts in all namespaces:  console=True
    FOR  ${service_account}  IN  @{service_accounts}
        Log  ${service_account}  console=True
    END	
