*** Settings ***
Resource          ./hpa_kw.robot

*** Test Cases ***
List Horizontal Pod Autoscalers in namespace
    [Tags]    other    prerelaese
    List Horizontal Pod Autoscalers by namespace  kubelib-tests