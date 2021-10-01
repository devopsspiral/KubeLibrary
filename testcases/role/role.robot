*** Settings ***
Resource          ./role_kw.robot

*** Test Cases ***
Role test case example
    [Tags]    others    prerelease
    List all roles in namespace  default

Working on Role
    [Tags]    other    prerelease
    List all roles in namespace    default    
    Edit obtained role    mini-role
    Create new role in namespace    default    
    Delete created role in namespace    mini-role    default
