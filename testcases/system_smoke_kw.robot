*** Settings ***
Library           Collections
Library           RequestsLibrary
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../src/KubeLibrary/KubeLibrary.py

*** Keywords ***
kubernetes API responds
    [Documentation]  Check if API response code is 200
    ${ping}=    k8s_api_ping
    Should Be Equal As integers    ${ping}[1]    200

kubernetes has "${number}" healthy nodes
    ${node_count}=    get_healthy_nodes_count
    Should Be Equal As integers    ${node_count}    ${number}

getting all pods names in "${namespace}"
    @{namespace_pods_names}=    get_pod_names_in_namespace    .*    ${namespace}
    Log    ${namespace_pods_names}
    Set Test Variable    ${namespace_pods_names}

all pods in "${namespace}" are running or succeeded
    FOR    ${name}    IN    @{namespace_pods_names}
         ${status}=    get_pod_status_in_namespace    ${name}    ${namespace}
         Should Be True     '${status}'=='Running' or '${status}'=='Succeeded'
    END

accessing "${pattern}" excluding "${exclude}" container images version in "${namespace}"
    @{pods_images}=    get_pods_images_in_namespace    ${pattern}   ${namespace}    ${exclude}
    Log    ${pods_images}
    Set Test Variable    ${pods_images}

"${version}" version is used
    FOR    ${Item}    IN    @{pods_images}
         Should Be Equal As Strings    ${Item}    ${version}
    END

getting kubelet version
    @{node_kubelet_versions}=    get_kubelet_version
    Log    ${node_kubelet_versions}
    Set Test Variable    ${node_kubelet_versions}

Kubernetes version is correct
    FOR    ${Item}    IN    @{node_kubelet_versions}
         Should Be Equal As Strings    ${Item}    ${KUBELET_VERSION}
    END

"${service}" has "${number}" replicas
    ${count}=    Get Match Count    ${namespace_pods_names}    ${service}
    Should Be True    ${number} == ${count}

"${service}" has at least "${number}" replicas
    ${count}=    Get Match Count    ${namespace_pods_names}    ${service}
    Should Be True    ${count} >= ${number}

getting pvcs in "${namespace}"
    @{namespace_pvcs}=    get_pvc_in_namespace    ${namespace}
    Log    ${namespace_pvcs}
    Set Test Variable    ${namespace_pvcs}

"${service}" has "${number}" pvcs
    ${count}=    Get Match Count    ${namespace_pvcs}    ${service}
    Should Be True    ${number} == ${count}

getting pvc size for "${volume}" in "${namespace}"
    ${pvc}=    get_pvc_capacity    ${volume}    ${namespace}
    Log    ${pvc}
    ${pvc_size}=    Set Variable    ${pvc.status.capacity["storage"]}
    Set Test Variable    ${pvc_size}

pvc size is "${size}"
	Should Be Equal As Strings     ${size}       ${pvc_size}

getting services in "${namespace}"
    @{namespace_services}=    get_services_in_namespace    ${namespace}
    Log    ${namespace_services}
    Set Test Variable    ${namespace_services}

getting service "${service}" details in "${namespace}"
    ${service_details}=    get_service_details_in_namespace    ${service}    ${namespace}
    Set Test Variable    ${service_details}

service is exposed on "${port}" port
    Should Be Equal As integers    ${service_details.spec.ports[0].port}    ${port}

service has "${type}" type
    Should Be Equal As Strings    ${service_details.spec.type}    ${type}

service has LB ip assigned
    Should Not Be Equal As Strings    ${service_details.status.load_balancer.ingress[0].ip}    None

getting "${endpoint}" endpoint in "${namespace}"
    ${endpoint_details}=    get_endpoints_in_namespace    ${endpoint}    ${namespace}
    Set Test Variable    ${endpoint_details}

endpoint points to "${pod}" pod
    Should Match    ${endpoint_details.subsets[0].addresses[0].target_ref.name}    ${pod}

"${service}" service ip and port in "${namespace}" is known
    ${service_details}=    get_service_details_in_namespace    ${service}    ${namespace}
    ${service_ip}=    Set Variable    ${service_details.status.load_balancer.ingress[0].ip}
    ${service_port}=    Set Variable    ${service_details.spec.ports[0].port}
    Set Test Variable    ${service_ip}
    Set Test Variable    ${service_port}

session is created
    Create Session    service_session    http://${service_ip}:${service_port}

service is responding on path "${path}"
    ${resp}=    Get Request    service_session    ${path}
    Should Be Equal As Strings    ${resp.status_code}    200
