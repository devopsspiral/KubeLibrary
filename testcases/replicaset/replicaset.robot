*** Settings ***
Resource          ./replicaset_kw.robot

*** Test Cases ***
Replicaset test case example
    [Tags]    replicaset    other
    List all replicasets in namespace  default
