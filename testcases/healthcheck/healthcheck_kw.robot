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
    FOR    ${i}    IN RANGE    2
	      Remove from List    ${RESPONSE}    -1
    END

    FOR    ${ELEMENT}    IN    @{RESPONSE}
	    Should Be True      "ok" in """${ELEMENT}""" 
	    log to console  \n ${ELEMENT}
    END
	
