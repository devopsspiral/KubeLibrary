*** Settings ***
Resource          ./pvc_kw.robot

*** Test Cases ***
List Persitent Volume Claims by label
    [Tags]    grafana
    List pvcs by label  default  app=grafana

List Persitent Volume Claims by pattern
    [Tags]    grafana
    List pvcs by pattern  .*  default