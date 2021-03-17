*** Settings ***
Resource          ./role_kw.robot

*** Test Cases ***
Role test case example
    [Tags]    others    prerelease
    List all roles in namespace  default
    List all role bindings in namespace  default
