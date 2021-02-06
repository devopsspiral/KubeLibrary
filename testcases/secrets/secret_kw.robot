*** Settings ***
Library           Collections
Library           RequestsLibrary
# For regular execution
### Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
Library           ../../src/KubeLibrary/KubeLibrary.py  

*** Keywords ***
List all secrets in namespace
    [Arguments]  ${namespace}  ${label}=${EMPTY}
    @{namespace_secrets}=  Get Secrets In Namespace    .*  ${namespace}  ${label}
    Log  \nSecrets in namespace ${namespace}:  console=True
    FOR  ${secret}  IN  @{namespace_secrets}
        Log  ${secret.metadata.name}  console=True
    END

# List all key value pairs in configmap
#     [Arguments]  ${configmap_name}  ${namespace}
#     @{namespace_configmaps}=  Get Configmaps In Namespace    ^${configmap_name}$  ${namespace}
#     Log  \nList of key value pairs in configmap ${configmap_name}:  console=True
#     FOR  ${configmap}  IN  @{namespace_configmaps}
#         Log key value pairs  ${configmap.data}
#     END

# Log key value pairs
#     [Arguments]  ${configmap_data}
#     FOR  ${key}  ${value}  IN  &{configmap_data}
#         Log  ${key} = ${value}  console=True
#     END


