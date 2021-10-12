*** Settings ***
Resource          ./replicaset_kw.robot

*** Test Cases ***
Replicaset test case example
    [Tags]    replicaset    other
    List all replicasets in namespace  default

Lsit All Replica Set
    [Tags]    others
    List all replica sets in all namespaces
