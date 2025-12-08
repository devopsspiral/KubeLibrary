*** Settings ***
Resource          ./cluster_role_kw.robot

*** Test Cases ***
Cluster_role test case example
    [Tags]    other
    List all cluster_roles
    List all cluster_role_bindings
