*** Settings ***
Library           Collections
Library           RequestsLibrary
# For regular execution
#Library           KubeLibrary
# For incluster execution
Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all jobs in namespace
    [Arguments]  ${namespace}
    @{namespace_jobs}=  Get Jobs In Namespace    .*  ${namespace}
    Log  \nJobs in namespace ${namespace}:  console=True
    FOR  ${job}  IN  @{namespace_jobs}
        Log  ${job.metadata.name}  console=True
        Set Global Variable    ${job_name}    ${job.metadata.name}
    END

List labels of job
    [Arguments]  ${job_name}  ${namespace}
    @{namespace_jobs}=  Get Jobs In Namespace    ^${job_name}$  ${namespace}
    Log  \nList labels in job ${job_name}:  console=True
    FOR  ${job}  IN  @{namespace_jobs}
        Log  Labels in ${job.metadata.labels}  console=True
        Dictionary Should Contain Item    ${job.metadata.labels}    TestLabel    mytestlabel
        ...  msg=Expected labels do not match.
    END

Get pod created by job
    [Arguments]  ${job_name}  ${namespace}
    @{namespace_pods}=  Get Pods In Namespace  ${job_name}  ${namespace}
    FOR  ${pod}  IN  @{namespace_pods}
        Log  \nList labels in pod ${pod.metadata.name}:  console=True
        Log  ${pod.metadata.labels}  console=True
        Dictionary Should Contain Item    ${pod.metadata.labels}    job-name    busybox-job
        ...  msg=Could not find job name label.
    END


