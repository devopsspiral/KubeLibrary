*** Settings ***
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
List all daemonsets
    [Arguments]  ${namespace} 
    @{namespace_daemonsets}=  Get Daemonsets In Namespace    ${namespace}  
    Length Should Be  ${namespace_daemonsets}  1
    Log  \nDaemonsets ${namespace_daemonsets}:  console=True

List daemonsets filtered by label
    [Arguments]  ${namespace}   ${label}
    @{namespace_daemonsets}=  Get Daemonsets In Namespace    ${namespace}    ${label}	
	Length Should Be  ${namespace_daemonsets}  1
    Log  \nDaemonsets with label ${label} ${namespace_daemonsets}:  console=True
