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
