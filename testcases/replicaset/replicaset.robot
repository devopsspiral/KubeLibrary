*** Settings ***
Resource          ./replicaset_kw.robot

*** Test Cases ***
Replicaset test case example
    [Tags]    replicaset  prerelease  
    List all replicasets in namespace  default
