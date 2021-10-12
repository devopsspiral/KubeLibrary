*** Settings ***
Resource          ./service_kw.robot

*** Test Cases ***
Services by label
    [Tags]    other
    List services by label  kubelib-tests  app.kubernetes.io/instance=kubelib-test

Lsit All Service
    [Tags]    others
    List all services in all namespaces
