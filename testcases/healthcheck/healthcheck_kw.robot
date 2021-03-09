*** Settings ***
Library           Collections
Library           RequestsLibrary
Library           String
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
Healthcheck
    @{RESPONSE}=  Get Healthcheck	
    @{ENDPOINTS} =  Split String    ${RESPONSE}[0]    \n
    FOR    ${ELEMENT}    IN    @{ENDPOINTS}
        Should Be True      "ok" or "healthz check passed" in """${ELEMENT}""" 
    END
    Should Be Equal As Strings  ${RESPONSE}[1]  200

Query Health API
    [Arguments]  ${endpoint}=/livez  ${verbose}=True
    ${response}=    get_healthcheck  ${endpoint}  ${verbose}
    Should Be Equal As integers  ${response}[1]  200
    [Return]  ${response}

Health API Template
    [Documentation]  Checks both /readyz/${endpoint} and /livez/${endpoint}
    [Arguments]  ${endpoint}  ${expected}
    ${readyz}=  Query Health API  /readyz/${endpoint}
    ${livez}=  Query Health API  /livez/${endpoint}
    Should Match Regexp  ${readyz}[0]  ${expected}
    Should Match Regexp  ${livez}[0]  ${expected}
