*** Settings ***
Resource          ./secret_kw.robot

*** Test Cases ***
Secrets test case example
    [Tags]    grafana    prerelease
    List all secrets in namespace  default
    Read grafana secrets
