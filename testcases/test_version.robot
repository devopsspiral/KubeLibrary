*** Settings ***
Library    KubeLibrary

*** Test Cases ***
Kubernetes Cluster Version Test
    [Tags]    prerelease
    Get Kubernetes Cluster Version

*** Keywords ***
Get Kubernetes Cluster Version
    ${version}    K8s Version
    Log    \nk8s version output:    console=True
    FOR    ${key}    ${value}    IN    &{version}
        Log    ${key}: ${value}    console=True
    END
    Log    Just the k8s cluster version: ${version['gitVersion']}    console=True