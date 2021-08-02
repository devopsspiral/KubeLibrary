*** Settings ***
Library           BuiltIn
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