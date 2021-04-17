*** Settings ***
Resource          ./namespace_kw.robot

*** Test Cases ***
Namespace test case example
    [Tags]    other    prerelease
    List all namespaces
    List namespaces filtered by label