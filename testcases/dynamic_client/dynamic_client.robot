*** Settings ***
Resource          ./dynamic_client_kw.robot

*** Test Cases ***
Dynamic client test case example
    [Tags]    dynamic-client
    ${resources}=    discover resources    default
    Log To Console     ${resources}
