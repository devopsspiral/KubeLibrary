*** Settings ***
Resource          ./sts_kw.robot

*** Test Cases ***
Statefulset test case example
    [Tags]    statefulset    other
    List all statefulsets in namespace  default
