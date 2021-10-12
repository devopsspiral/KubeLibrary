*** Settings ***
Resource          ./role_kw.robot

*** Test Cases ***
Role test case example
    [Tags]    other
    List all roles in namespace  default
    List all role bindings in namespace  default

Working on Role
    [Tags]    other    prerelease
    List all roles in namespace    default    
    Edit obtained role    mini-role
    Create new role in namespace    default    
    Delete created role in namespace    mini-role    default

Lsit All Role
    [Tags]    grafana
    List all roles in all namespaces
