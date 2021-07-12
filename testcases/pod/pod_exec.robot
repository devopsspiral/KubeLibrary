*** Settings ***
Library           OperatingSystem
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

Documentation    These test cases demo the use of executing commands in containers.

*** Variables ***
${job_name}     busybox-job
${container}    busybox
${namespace}    kubelib-tests

*** Test Cases ***
Get pod created by busybox-job
    [Tags]    other    prerelease
    @{namespace_pods}=  Get Pods In Namespace  ${job_name}  ${namespace}
    Set Global Variable  ${pod}  ${namespace_pods[0].metadata.name}
    Wait Until Keyword Succeeds  2min  5sec  Pod is running

Return container uptime
    [Tags]    other    prerelease
    ${resp}  Execute in Container  uptime  ${pod}  ${container}  ${namespace}
    Log  \nContainer uptime is: ${resp}  console=True

Copy file from container
    [Tags]    other    prerelease
    ${file}  Set Variable  resolv.conf
    ${exec_command}  Create List  cat  /etc/${file}
    ${resp}  Execute in Container  ${exec_command}  ${pod}  ${container}  ${namespace}
    Create File  ${file}  ${resp}

Create a file in container
    [Tags]    other    prerelease
    ${file}  Set Variable  testfile.txt
    ${exec_command}  Create List  touch  /tmp/${file}
    ${resp}  Execute in Container  ${exec_command}  ${pod}  ${container}  ${namespace}

Check if file exists in container
    [Tags]    other    prerelease
    ${file}  Set Variable  testfile.txt
    ${exec_command}  Create List  /bin/ash  -c  FILE=/tmp/${file} && [ -f $FILE ] && echo "$FILE exists."
    ${resp}  Execute in Container  ${exec_command}  ${pod}  ${container}  ${namespace}
    Should be equal  ${resp.strip()}  /tmp/${file} exists.

Return environment variables from a container
    [Tags]    other    prerelease
    ${resp}  Execute in Container  env  ${pod}  ${container}  ${namespace}
    Log  \nList of env variables inside ${pod}:\n${resp}  console=True
    
*** Keywords ***
Pod is running
    ${status}=    get_pod_status_in_namespace    ${pod}    ${namespace}
    Should Be True     '${status}'=='Running'