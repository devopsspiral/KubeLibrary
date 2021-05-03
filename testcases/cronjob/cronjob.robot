*** Settings ***
Resource          ./cronjob_kw.robot

*** Test Cases ***
Job test case example
    [Tags]    other    prerelease
    List all cron jobs in namespace  kubelib-tests

Jobs by label
    [Tags]    other    prerelease
    List cron jobs with label  ${cron_job_name}  kubelib-tests  TestLabel=mytestlabel
	
Working on Cron Job
    [Tags]    other    prerelease
    List all cron jobs in namespace    kubelib-tests
    Edit obtained cron job    test-cronjob
    Create new cron job in namespace    kubelib-tests
    Delete created cron job in namespace    test-cronjob    kubelib-tests
    
