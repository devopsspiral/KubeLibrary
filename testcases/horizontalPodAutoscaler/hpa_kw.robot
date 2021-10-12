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
List Horizontal Pod Autoscalers by namespace
    [Arguments]  ${namespace}  
    @{namespace_hpas}=  List Namespaced Horizontal Pod Autoscaler    ${namespace}  
    FOR  ${hpa}  IN  @{namespace_hpas}
        ${hpa_details}=  Read Namespaced Horizontal Pod Autoscaler  ${hpa}  ${namespace}
        Should be Equal as Strings  ${hpa_details.spec.max_replicas}  5
        Should be Equal as Strings  ${hpa_details.spec.min_replicas}  1
        Should be Equal as Strings  ${hpa_details.spec.target_cpu_utilization_percentage}  50
    END


