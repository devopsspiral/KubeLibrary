*** Settings ***
Library           Collections
Library           RequestsLibrary
Library           String
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***

waited for pods matching "${name_pattern}" in namespace "${namespace}" to be READY
    Wait Until Keyword Succeeds    ${KLIB_POD_TIMEOUT}    ${KLIB_POD_RETRY_INTERVAL}   pod "${name_pattern}" status in namespace "${namespace}" is READY

pod "${name_pattern}" status in namespace "${namespace}" is READY 
    @{namespace_pods}=    list_namespaced_pod_by_pattern  ${name_pattern}    ${namespace}
    @{namespace_pods_names}=    Filter Names    ${namespace_pods}
    ${num_of_pods}=    Get Length    ${namespace_pods_names}
    Should Be True    ${num_of_pods} >= 1    No pods matching "${name_pattern}" found
    FOR    ${pod}    IN    @{namespace_pods_names}
        ${status}=    read_namespaced_pod_status    ${pod}    ${namespace}
        ${conditions}=    Filter by Key    ${status.conditions}    type    Ready
        Should Be True     '${conditions[0].status}'=='True'
    END

getting pods matching "${name_pattern}" in namespace "${namespace}"
    @{namespace_pods}=    list_namespaced_pod_by_pattern  ${name_pattern}    ${namespace}
    Set Test Variable    ${namespace_pods}

getting pods matching label "${label}" in namespace "${namespace}"
    @{namespace_pods}=    list_namespaced_pod_by_pattern  .*    ${namespace}  label_selector=${label}
    Set Test Variable    ${namespace_pods}
    ${label_key}=  Fetch From Left    ${KLIB_POD_LABELS}    =
    ${label_value}=  Fetch From Right    ${KLIB_POD_LABELS}    =
    Set Test Variable    ${KLIB_POD_LABELS}    {"${label_key}": "${label_value}"}

all pods containers are using "${container_image}" image
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    @{containers_images}=    filter_containers_images    ${containers}
    FOR    ${item}    IN    @{containers_images}
        Should Contain    ${item}    ${container_image}
    END

pods have "${pod_replicas}" replicas
    ${count}=    Get Length   ${namespace_pods}
    Should Be True    ${count} == ${pod_replicas}

pods containers were not restarted
    @{containers_statuses}=    filter_pods_containers_statuses_by_name    ${namespace_pods}    .*
    FOR    ${container_status}    IN    @{containers_statuses}
        Should Be True    ${container_status.restart_count} == 0
    END

pods have labels "${pod_labels}"
    FOR    ${pod}    IN    @{namespace_pods}
        ${assertion}=    assert_pod_has_labels    ${pod}    ${pod_labels}
        Should Be True    ${assertion}
    END

pods have annotations "${pod_annotations}"
    FOR    ${pod}    IN    @{namespace_pods}
        ${assertion}=    assert_pod_has_annotations    ${pod}    ${pod_annotations}
        Should Be True    ${assertion}
    END

pods containers have resource requests cpu "${container_resource_requests_cpu}"
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    @{containers_resources}=    filter_containers_resources    ${containers}
    FOR    ${item}    IN    @{containers_resources}
        Should Be Equal As Strings    ${item.requests['cpu']}    ${container_resource_requests_cpu}
    END

pods containers have resource requests memory "${container_resource_requests_memory}"
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    @{containers_resources}=    filter_containers_resources    ${containers}
    FOR    ${item}    IN    @{containers_resources}
        Should Be Equal As Strings    ${item.requests['memory']}    ${container_resource_requests_memory}
    END

pods containers have resource limits cpu "${container_resource_limits_cpu}"
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    @{containers_resources}=    filter_containers_resources    ${containers}
    FOR    ${item}    IN    @{containers_resources}
        Should Be Equal As Strings    ${item.limits['cpu']}    ${container_resource_limits_cpu}
    END

pods containers have resource limits memory "${container_resource_requests_memory}"
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    @{containers_resources}=    filter_containers_resources    ${containers}
    FOR    ${item}    IN    @{containers_resources}
        Should Be Equal As Strings    ${item.limits['memory']}    ${container_resource_requests_memory}
    END

pods containers have env variables "${container_env_vars}"
    @{containers}=    filter_pods_containers_by_name    ${namespace_pods}    .*
    FOR    ${container}    IN    @{containers}
        ${assertion}=    assert_container_has_env_vars    ${container}    ${container_env_vars}
        Should Be True    ${assertion}
    END

logs of pod can be retrived
    Set Test Variable    ${POD_NAME}    ${namespace_pods[0].metadata.name}
    ${pod_logs}=  Read namespaced pod log  ${POD_NAME}  ${KLIB_POD_NAMESPACE}  busybox  since_seconds=1000
    Log  ${pod_logs}  console=True
    Set Test Variable    ${POD_LOGS}    ${pod_logs}

logs contain expected string
    Should Contain    ${POD_LOGS}    I am