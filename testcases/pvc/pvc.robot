*** Settings ***
Resource          ./pvc_kw.robot

*** Test Cases ***
List Persitent Volume Claims by label
    [Tags]    grafana
    List pvcs by label  default  app=grafana

Lsit All Persistent Volume Claim
    [Tags]    grafana
    List all persistent_volume_claim in all namespaces
