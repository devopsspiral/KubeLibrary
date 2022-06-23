*** Settings ***
Resource          ./custom_definitions_kw.robot

*** Variables ***
${crds}    repos.configmanagement.gke.io syncs.configmanagement.gke.io
${crd_name}    repos.configmanagement.gke.io

*** Test Cases ***
Check All The Custom Resource Definitions Exist
    [Documentation]    Test all the given Custom Resource Definitions exist.
    CRD contains: ${crds}

Check The Given Custom Resource Definition Exist
    [Documentation]    Test the given Custom Resource Definition exists.
    CRD ${crd_name} exists
