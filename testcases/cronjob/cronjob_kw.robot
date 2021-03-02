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


