*** Settings ***
Resource          ./deployment_kw.robot

*** Test Cases ***
Deployment test case example
    [Tags]    grafana
    List all deployments in namespace  default
    Show Grafana Deployment
    Assert Replica Status
