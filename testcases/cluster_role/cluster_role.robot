*** Settings ***
Resource          ./cluster_role_kw.robot

*** Test Cases ***
Cluster_role test case example
    [Tags]    other    prerelease 
    List all cluster_role
    List all cluster_role_binding
