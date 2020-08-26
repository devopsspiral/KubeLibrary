*** Settings ***
Resource          ./namespace_kw.robot

*** Test Cases ***
Namespace test case example
    [Tags]    other
    List all namespaces
    List namespaces filtered by label