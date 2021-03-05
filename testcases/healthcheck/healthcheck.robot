*** Settings ***
Library           Collections
Resource          ./healthcheck_kw.robot
Default Tags      prerelease

*** Test Cases ***
Healthcheck
    [Tags]    other
    Healthcheck

Health API Reports Ok
    [Tags]    cluster    smoke
    ${response}=  Query Health API  verbose=False
    Should Be equal As Strings  ${response}[0]  ok

Health API Reports Checks Passed With Verbose
    [Tags]    cluster    smoke
    ${response}=  Query Health API

    # healthz < 1.20, livez >=1.20
    Should Match Regexp  ${response}[0]  (livez|healthz) check passed

Health API Reports Ok For informer-sync
    [Tags]    cluster    smoke
    ${response}=  Query Health API  /readyz/informer-sync
    Should Be equal As Strings  ${response}[0]  ok

Health API Reports Ok For shutdown
    [Tags]    cluster    smoke
    ${response}=  Query Health API  /readyz/shutdown
    Should Be equal As Strings  ${response}[0]  ok

Health API Reports Ok For ping
    [Tags]    cluster    smoke
    [Template]  Health API Template
    ping  ok

Health API Reports Ok For log
    [Tags]    cluster    smoke
    [Template]  Health API Template
    log  ok

Health API Reports Ok For etcd
    [Tags]    cluster    smoke
    [Template]  Health API Template
    etcd  ok

Health API Reports Ok For poststarthook/start-kube-apiserver-admission-initializer
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/start-kube-apiserver-admission-initializer  ok

Health API Reports Ok For poststarthook/generic-apiserver-start-informers
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/generic-apiserver-start-informers  ok

Health API Reports Ok For poststarthook/max-in-flight-filter
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/max-in-flight-filter  ok

Health API Reports Ok For poststarthook/start-apiextensions-informers
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/start-apiextensions-informers  ok

Health API Reports Ok For poststarthook/start-apiextensions-controllers
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/start-apiextensions-controllers  ok

Health API Reports Ok For poststarthook/crd-informer-synced
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/crd-informer-synced  ok

Health API Reports Ok For poststarthook/bootstrap-controller
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/bootstrap-controller  ok

Health API Reports Ok For poststarthook/scheduling/bootstrap-system-priority-classes
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/scheduling/bootstrap-system-priority-classes  ok

Health API Reports Ok For poststarthook/start-cluster-authentication-info-controller
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/start-cluster-authentication-info-controller  ok

Health API Reports Ok For poststarthook/aggregator-reload-proxy-client-cert
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/aggregator-reload-proxy-client-cert  ok

Health API Reports Ok For poststarthook/start-kube-aggregator-informers
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/start-kube-aggregator-informers  ok

Health API Reports Ok For poststarthook/apiservice-registration-controller
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/apiservice-registration-controller  ok

Health API Reports Ok For poststarthook/apiservice-status-available-controller
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/apiservice-status-available-controller  ok

Health API Reports Ok For poststarthook/kube-apiserver-autoregistration
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/kube-apiserver-autoregistration  ok

Health API Reports Ok For autoregister-completion
    [Tags]    cluster    smoke
    [Template]  Health API Template
    autoregister-completion  ok

Health API Reports Ok For poststarthook/apiservice-openapi-controller
    [Tags]    cluster    smoke
    [Template]  Health API Template
    poststarthook/apiservice-openapi-controller  ok
