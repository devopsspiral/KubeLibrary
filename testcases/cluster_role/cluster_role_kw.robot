*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all cluster_role
    @{cluster_role_list}=  Get Cluster_role
    Log  \nCluster_role ${cluster_role_list}:  console=True

List all cluster_role_binding
    @{cluster_role_binding_list}=  Get Cluster_role_binding
    Log  \nCluster_role_binding ${cluster_role_binding_list}:  console=True
