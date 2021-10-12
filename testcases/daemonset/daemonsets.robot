*** Settings ***
Resource          ./daemonsets_kw.robot

*** Test Cases ***
Daemonsets test case example
    [Tags]    other
    List all daemonsets  kubelib-tests  
    List daemonsets filtered by label  kubelib-tests  TestLabel=mytestlabel

Lsit All Daemon Set
    [Tags]    others
    List all daemon sets in all namespaces
