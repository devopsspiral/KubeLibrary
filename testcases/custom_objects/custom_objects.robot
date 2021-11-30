*** Settings ***
Library         KubeLibrary

*** Test Cases ***
Get List Of Cluster Custom Objects
    [Tags]  smoke
    ${prio_classes}=  List Cluster Custom Object   scheduling.k8s.io   v1   priorityclasses
    # Log To Console  ${prio_classes}
    Should Be Equal As Strings  ${prio_classes}[kind]  PriorityClassList

Get Cluster Custom Object
    [Tags]  smoke
    ${prio_class}=  Get Cluster Custom Object  scheduling.k8s.io   v1   priorityclasses  system-node-critical
    Should Be Equal As Strings  ${prio_class}[metadata][name]    system-node-critical
    Should Be Equal As Strings  ${prio_class}[kind]  PriorityClass

Get Namespaced Custom Object
    [Tags]  smoke
    ${fo}=  Get Namespaced Custom Object   discovery.k8s.io  v1beta1  default  endpointslices  kubernetes
    Should Be Equal As Strings  ${fo}[metadata][name]    kubernetes
    Should Be Equal As Strings  ${fo}[addressType]  IPv4
