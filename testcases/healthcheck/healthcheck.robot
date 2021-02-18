*** Settings ***
Resource          ./healthcheck_kw.robot

*** Test Cases ***
Healthcheck
    [Tags]    other
    Healthcheck
	
