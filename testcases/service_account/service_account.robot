*** Settings ***
Resource          ./service_account_kw.robot

*** Test Cases ***
Listing Service Accounts
    [Tags]    other
    List all service accounts for matching name pattern in namespace    .*     kubelib-tests
    List all service accounts for matching name pattern in namespace with label    .*    kubelib-tests    TestLabel=mytestlabel

Working on Service Accounts
    [Tags]    other
    List all service accounts for matching name pattern in namespace    default     kubelib-tests
    Edit obtained service account    test-sa
    Create new service account in namespace    kubelib-tests
    Delete created service account in namespace    test-sa    kubelib-tests