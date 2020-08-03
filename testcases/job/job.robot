*** Settings ***
Resource          ./job_kw.robot

*** Test Cases ***
Job test case example
    [Tags]    other
    List all jobs in namespace  kubelib-tests
    List labels of job  ${job_name}  kubelib-tests
    Get pod created by job  ${job_name}  kubelib-tests
