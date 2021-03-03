*** Settings ***
Resource          ./daemonsets_kw.robot

*** Test Cases ***
Daemonsets test case example
    [Tags]    other    prerelease
    List all daemonsets  default  
    List daemonsets filtered by label  default  test=test
