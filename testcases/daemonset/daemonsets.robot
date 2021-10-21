*** Settings ***
Resource          ./daemonsets_kw.robot

*** Test Cases ***
Daemonsets test case example
    [Tags]    other
    List all daemonsets  kubelib-tests  
    List daemonsets filtered by label  kubelib-tests  TestLabel=mytestlabel
