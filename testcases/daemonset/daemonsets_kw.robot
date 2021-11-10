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
    @{namespace_daemonsets}=  List Namespaced Daemon Set    ${namespace}  
    Length Should Be  ${namespace_daemonsets}  1
    Log  \nDaemonsets ${namespace_daemonsets}:  console=True
    FOR  ${daemonset}  IN  @{namespace_daemonsets}
        Wait Until Keyword Succeeds  1min  5sec  Check Daemonset readiness  ${daemonset.metadata.name}  ${namespace} 
    END

Check Daemonset readiness
    [Arguments]  ${daemonset}  ${namespace}
    ${daemonset_details}=  Read Namespaced Daemon Set  ${daemonset}  ${namespace}
    Log  \nDaemonset - ${daemonset}:  console=True
    Log  \n\tDesired Number Scheduled : ${daemonset_details.status.desired_number_scheduled}   console=True
    Log  \n\tNumber Ready : ${daemonset_details.status.number_ready} :  console=True
    Should be True  ${daemonset_details.status.number_ready} > 0
    Should be equal   ${daemonset_details.status.desired_number_scheduled}    ${daemonset_details.status.number_ready}


List daemonsets filtered by label
    [Arguments]  ${namespace}   ${label}
    @{namespace_daemonsets}=  List Namespaced Daemon Set    ${namespace}    ${label}	
	Length Should Be  ${namespace_daemonsets}  1
    Log  \nDaemonsets with label ${label} ${namespace_daemonsets}:  console=True
    FOR  ${daemonset}  IN  @{namespace_daemonsets}
        ${daemonset_details}=  Read Namespaced Daemon Set  ${daemonset.metadata.name}  ${namespace}
        Log  \nDaemonset - ${daemonset}:  console=True
        Log  \n\tDesired Number Scheduled : ${daemonset_details.status.desired_number_scheduled}   console=True
        Log  \n\tNumber Ready : ${daemonset_details.status.number_ready} :  console=True
        Should be equal   ${daemonset_details.status.desired_number_scheduled}    ${daemonset_details.status.number_ready}
    END
