*** Settings ***
Resource          ./ingress_kw.robot

*** Test Cases ***
Ingresses by label
    [Tags]    other
    List ingresses by label  kubelib-tests  app.kubernetes.io/instance=kubelib-test

Ingresses in namespace
    [Tags]    other    prerelease
    List all ingresses in namespace  kubelib-tests

Working on Ingress
    [Tags]    other    prerelease
    List all ingresses in namespace    kubelib-tests
    Edit obtained ingress    my-ingress
    Create new ingress in namespace    kubelib-tests
    Delete created ingress in namespace    my-ingress    kubelib-tests

	
