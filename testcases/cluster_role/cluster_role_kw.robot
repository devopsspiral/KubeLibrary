*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all cluster_roles
    @{cluster_roles_list}=  List Cluster Role
    @{cluster_roles_name_list}=    Filter Names    ${cluster_roles_list}
    Log  \nCluster_role ${cluster_roles_name_list}:  console=True

List all cluster_role_bindings
    @{cluster_role_bindings_list}=  List Cluster Role Binding
    @{cluster_role_bindings_names_list}=    Filter Names    ${cluster_role_bindings_list}
    Log  \nCluster_role_binding ${cluster_role_bindings_names_list}:  console=True
