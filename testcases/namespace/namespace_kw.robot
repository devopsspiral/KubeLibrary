*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all namespaces
    @{namespaces_list}=  List Namespace
    @{namespace_names}=    Filter Names    ${namespaces_list}
    Log  \nNamespaces ${namespace_names}:  console=True

List namespaces filtered by label
    @{namespaces_list}=  List Namespace  label_selector=test=test
    @{namespace_names}=    Filter Names    ${namespaces_list}
    Log  \nNamespaces with label test=test ${namespace_names}:  console=True



