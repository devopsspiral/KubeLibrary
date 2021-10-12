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
List all cron jobs in namespace
    [Arguments]  ${namespace}
    @{namespace_cron_jobs}=  Get Cron Jobs In Namespace    ${namespace}
    Log  \nCron Jobs in namespace ${namespace}:  console=True
    Length Should Be  ${namespace_cron_jobs}  1
    FOR  ${cron_job}  IN  @{namespace_cron_jobs}
        ${cronjob_details}=  Get Cron Job Details In Namespace  ${cron_job}  ${namespace}
        Log  ${cronjob_details.metadata.name}  console=True
        Set Global Variable    ${cron_job_name}    ${cronjob_details.metadata.name}
	Set Global Variable    ${cron_job}    ${cronjob_details}
    END

List cron jobs with label
    [Arguments]  ${cron_job_name}  ${namespace}  ${label}
    @{namespace_cron_jobs}=  Get Cron Jobs In Namespace    ${namespace}  ${label}
    Log  \nList labels in cron job ${cron_job_name}:  console=True
    Length Should Be  ${namespace_cron_jobs}  1
    FOR  ${cron_job}  IN  @{namespace_cron_jobs}
        ${cron_job_details}=  Get Cron Job Details In Namespace  ${cron_job}  ${namespace}
        ${label_key}=  Fetch From Left    ${label}    =
        ${label_value}=  Fetch From Right    ${label}    =
        Log  Labels in ${cron_job_details.metadata.labels}  console=True
        Dictionary Should Contain Item    ${cron_job_details.metadata.labels}    ${label_key}  ${label_value}
        ...  msg=Expected labels do not match.
    END

Edit obtained cron job
    [Arguments]     ${cron_job_name}
    ${cron_job.metadata.name}=  Set Variable  ${cron_job_name}
    ${cron_job.metadata.resource_version}=  Set Variable  ${None}
    Set Global Variable    ${new_cron_job}    ${cron_job}

Create new cron job in namespace
    [Arguments]  ${namespace}
    Log  \nCreate new cron job in namespace ${namespace}  console=True
    ${new_cj}=    Create Cron Job In Namespace  ${namespace}  ${new_cron_job}
    Log  ${new_cj}  console=True

Delete created cron job in namespace
    [Arguments]  ${cron_job_name}    ${namespace}
    Log  \nDeletee cron job in namespace ${namespace}  console=True
    ${status}=    Delete Cron Job In Namespace  ${cron_job_name}    ${namespace}
    Log  ${status}

List all cron_jobs in all namespaces
    @{cron_jobs}=  Get Cron Job For All Namespaces
    Log  \ncron jobs in all namespaces:  console=True
    FOR  ${cron_job}  IN  @{cron_jobs}
        Log  ${cron_job}  console=True
    END
