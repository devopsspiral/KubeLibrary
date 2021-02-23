*** Settings ***
Resource          ./ingress_kw.robot

*** Test Cases ***
Ingresses by label
    [Tags]    other
    List ingresses by label  kubelib-tests  app.kubernetes.io/instance=kubelib-testcontrolplane
	
