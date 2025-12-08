**** Settings ***
Library          KubeLibrary
Library          Browser
Library          Collections

Documentation    This is an example test case to demo the abilities of the KubeLibrary.
...              This test will assert if all Kubernetes objects of a Grafana installation
...              were successfully install to the cluster. 
...                
...              Afterwards it will execute a UI test to perfom the login to the Grafana
...              dashboard with the url, username and password obtained from Kubernetes.
...               
...              This tests requires an installation of Grafana as described here:
...              https://github.com/devopsspiral/KubeLibrary#grafana-tests

*** Test Cases ***
Grafana is ready to be tested
    [Documentation]  Verifying all objects created by the helm deployment
    Check Grafana Deployment
    Assert Replica Status
    Grafana pods are running
    Check Grafana service
    Check Grafana secrets
    Check Grafana serviceaccounts

Obtain Grafana URL
    [Documentation]  Obtaining the url and port from the service object
    Get URL and port from service

Obtain Grafana login credentials
    [Documentation]  Obtaining username and password from the secrets object
    Read grafana secrets

Successful Login to Grafana
    [Documentation]  Login to the Grafana UI dashboard
    Login to Grafana

*** Keywords ***
Check Grafana Deployment
    @{namespace_deployments}=  List Namespaced Deployment By Pattern    grafana  default
    Length Should Be  ${namespace_deployments}  1
    FOR  ${deployment}  IN  @{namespace_deployments}
        Should be Equal   ${deployment.metadata.name}  grafana
        Set Global Variable  ${DEPLOYMENT}  ${deployment}
    END

Assert Replica Status
    Should be Equal  ${DEPLOYMENT.status.available_replicas}  ${DEPLOYMENT.status.replicas}
    ...  msg=Available replica count (${DEPLOYMENT.status.available_replicas}) doesn't match current replica count (${DEPLOYMENT.status.replicas}

Grafana pods are running
    Wait Until Keyword Succeeds    1min    5sec   Check grafana pod status

Check Grafana pod status 
    @{namespace_pods}=    Get Pod Names In Namespace    grafana    default
    Length Should Be  ${namespace_pods}  1
    FOR    ${pod}    IN    @{namespace_pods}
        ${status}=    Get Pod Status In Namespace    ${pod}    default
        Should Be True     '${status}'=='Running'
    END

Check Grafana service
    ${sevice_details}=  Get Service Details In Namespace  grafana  default
    Dictionary Should Contain Item    ${sevice_details.metadata.labels}    app.kubernetes.io/name  grafana
    ...  msg=Expected labels do not match.
    Should Be Equal    ${sevice_details.spec.type}    LoadBalancer
    ...  msg=Expected service type does not match.

Check Grafana secrets
    @{namespace_secrets}=  List Namespaced Secret By Pattern    grafana  default
    Length Should Be  ${namespace_secrets}  3

Check Grafana serviceaccounts
    @{namespace_service_accounts}=  List Namespaced Service Account By Pattern    grafana  default
    Length Should Be  ${namespace_service_accounts}  2
    FOR  ${service_account}  IN  @{namespace_service_accounts}
        Dictionary Should Contain Item    ${service_account.metadata.labels}    app.kubernetes.io/name  grafana
    END

Get URL and port from service
    ${sevice_details}=  Get Service Details In Namespace  grafana  default
    Set Global Variable  ${URL}  ${sevice_details.status.load_balancer.ingress[0].ip}
    Set Global Variable  ${PORT}  ${sevice_details.spec.ports[0].port}

Read grafana secrets
    @{namespace_secrets}=  List Namespaced Secret By Pattern    ^grafana$  default
    Length Should Be  ${namespace_secrets}  1
    ${GRAFANA_USER}=  Evaluate  base64.b64decode($namespace_secrets[0].data["admin-user"])  modules=base64
    Set Global Variable  ${GRAFANA_USER}  ${GRAFANA_USER}
    ${GRAFANA_PASSWORD}=  Evaluate  base64.b64decode($namespace_secrets[0].data["admin-password"])  modules=base64
    Set Global Variable  ${GRAFANA_PASSWORD}  ${GRAFANA_PASSWORD}

Login to Grafana
    New Browser  chromium  headless=${False}
    New Page     http://${URL}:${PORT}
    Wait Until Network Is Idle
    Sleep  20    #For live demo purposes
    Fill Text    //input[@name='user']      ${GRAFANA_USER}
    Fill Text    //input[@name='password']  ${GRAFANA_PASSWORD}
    Click        button
    Wait For Response  /api/dashboards/home
    Wait Until Network Is Idle
    Get Title    matches  Home - Grafana
    Get Text     //h1  matches  Welcome to Grafana
    Sleep  20    #For live demo purposes
