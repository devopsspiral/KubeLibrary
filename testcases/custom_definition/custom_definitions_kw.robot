*** Settings ***
Library           String
# For regular execution
Library           KubeLibrary
# For incluster execution
#Library           KubeLibrary    None    True    False
# For development
#Library           ../../src/KubeLibrary/KubeLibrary.py  ~/.kube/k3d

*** Keywords ***
CRD contains: ${crd_names}
    [Documentation]    Check the given CRD's exist!
    @{crd_name_list}=    Split String   ${crd_names}    ${SPACE}
    @{all_crds}=    List Cluster Custom Definition
    @{all_crd_names}=    Filter Names    ${all_crds}
    ${crd_num}=    Get Length    ${all_crd_names}
    Log    \nTotally ${crd_num} CRD(s) have been found.    console=True
    FOR    ${name}    IN    @{crd_name_list}
        Should Contain    ${all_crd_names}    ${name}
    END

CRD ${crd_name} exists
    [Documentation]    Check the given CRD exit!
    ${crd_detail}=    Read Cluster Custom Definition    ${crd_name}
    Should Be Equal    ${crd_detail.kind}    CustomResourceDefinition
Should Be Equal    ${crd_detail.metadata.name}    ${crd_name}
