*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all namespaces
    @{namespaces_list}=  Get Namespaces
    Log  \nNamespaces ${namespaces_list}:  console=True

List namespaces filtered by label
    @{namespaces_list}=  Get Namespaces  label_selector=test=test
    Log  \nNamespaces with label test=test ${namespaces_list}:  console=True



