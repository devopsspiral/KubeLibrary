*** Settings ***
Library           BuiltIn
Library           yaml
Library           OperatingSystem
Library           Collections
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
discover resources
    [Arguments]    ${namespace}
    ${deployments}=     get resource names    Deployment     apps/v1     ${namespace}
    ${statefulsets}=    get resource names    StatefulSet    apps/v1    ${namespace}
    ${cronjobs}=        get resource names    CronJob    batch/v1beta1    ${namespace}
    ${secrets}=         get resource names    Secret    v1    ${namespace}
    ${configmaps}=      get resource names    ConfigMap    v1    ${namespace}
    ${found}=           BuiltIn.evaluate    set(${deployments}) | set(${statefulsets}) | set(${cronjobs}) | set(${secrets}) | set(${configmaps})
    [return]    ${found}
get resource names
    [Arguments]     ${kind}    ${api_version}    ${namespace}
    ${resource_list}=     KubeLibrary.get    kind=${kind}     api_version=${api_version}     namespace=${namespace}
    ${names}=             KubeLibrary.get names from resource list    ${resource_list}
    [return]    ${names}
create pod
    [Arguments]     ${conf}
    KubeLibrary.create      api_version=v1      kind=Pod      body=${conf}
get specific pod
    [Arguments]     ${namespace}      ${label_selector}
    ${pods}=      KubeLibrary.get      api_version=v1      kind=Pod      namespace=${namespace}      label_selector=${label_selector}
    [return]      ${pods}
patch pod
    [Arguments]      ${pod}
    KubeLibrary.patch      api_version=v1      kind=Pod      body=${pod}
delete pod
    [Arguments]     ${namespace}      ${name}
    KubeLibrary.delete       api_version=v1    kind=Pod     name=${name}     namespace=${namespace}
replace svc
    [Arguments]     ${conf}
    KubeLibrary.replace    api_version=v1     kind=Service     body=${conf}
read conf
    [Arguments]     ${path}
    ${stream}=  Get Binary File      ${path}
    ${conf}=  yaml.Safe Load      ${stream}
    [return]      ${conf}
create svc
    [Arguments]    ${conf}
    KubeLibrary.create     api_version=v1     kind=Service     body=${conf}
delete svc
    [Arguments]    ${namespace}    ${name}
    KubeLibrary.delete     api_version=v1     kind=Service     name=${name}      namespace=${namespace}
get specific svc
    [Arguments]    ${namespace}    ${name}
    ${svc}=    KubeLibrary.get    api_version=v1     kind=Service     name=${name}     namespace=${namespace}
    [return]    ${svc}