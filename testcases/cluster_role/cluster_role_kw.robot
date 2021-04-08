*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all cluster_roles
    @{cluster_roles_list}=  Get Cluster_roles
    Log  \nCluster_role ${cluster_roles_list}:  console=True

List all cluster_role_bindings
    @{cluster_role_bindings_list}=  Get Cluster_role_bindings
    Log  \nCluster_role_binding ${cluster_role_bindings_list}:  console=True
