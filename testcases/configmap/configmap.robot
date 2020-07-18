*** Settings ***
Resource          ./configmap_kw.robot

*** Test Cases ***
Configmap test case example
    [Tags]    grafana
    List all configmaps in namespace  default
    List all key value pairs in configmap  grafana  default
