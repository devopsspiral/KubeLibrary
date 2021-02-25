*** Settings ***
Resource          ./reload-config_kw.robot

Documentation    This test requires two k8s clusters running according to 
...              the setup description in the README.md

*** Test Cases ***
Reload config test case example
    [Tags]    reload-config
    
    [Documentation]  The Keyword "Reload Config" allows the user to 
    ...  reload the KubeLibrary with different settings. With this 
    ...  one test can validate objects in different clusters.

    GIVEN Connected to cluster-1 
    THEN Cluster has namespace  test-ns-1
    AND Cluster has no namespace  test-ns-2

    WHEN Connected to cluster-2 
    THEN Cluster has namespace  test-ns-2
    AND Cluster has no namespace  test-ns-1

Authenticate using bearer token
    [Tags]    auth.bearer-token
    [Documentation]  Test authentication using brearer token

    WHEN Connected to cluster-1 using bearer token
    THEN Cluster has namespace  test-ns-1
    AND Cluster has no namespace  test-ns-2 