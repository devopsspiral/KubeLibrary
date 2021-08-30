*** Settings ***
Resource          ./dynamic_client_kw.robot

*** Test Cases ***
Dynamic client test case example
    [Tags]    dynamic-client
    ${resources}=    discover resources    default
    Log To Console     ${resources}
Dynamic client test case example 2
    [Tags]     dynamic-client
    ${conf}=     read conf     testcases/dynamic_client/resources/pod.yaml
    create pod     ${conf}
    sleep     5 seconds
    ${pods}=     get specific pod      default      app=myapp
    ${metadata}=     Get From Dictionary    ${conf}      metadata
    ${patched_labels}=     Create Dictionary      app=myapp       tested=true
    ${patched_metadata}=     Set To Dictionary     ${metadata}      labels      ${patched_labels}
    ${patched_pod}=      Set To Dictionary     ${conf}      metadata      ${patched_metadata}
    patch pod    ${patched_pod}
    sleep     5 seconds
    ${pods}=     get specific pod      default      tested=true
    Should Not Be Empty      ${pods.items}
    ${pods}=     get specific pod    default     tested=false
    Should Be Empty      ${pods.items}
    [Teardown]      delete pod     default     myapp-pod

Dynamic client test case example 3
    [Tags]     dynamic-client
    ${conf}=     read conf     testcases/dynamic_client/resources/svc.yaml
    create svc     ${conf}
    sleep    5 seconds
    ${svc}=    get specific svc    default     myservice
    ${new_selector}=     Create Dictionary     app=svc-lookup
    ${new_spec}=     Set To Dictionary     ${conf}[spec]     selector     ${new_selector}
    ${new_spec}=     Set To Dictionary     ${new_spec}      clusterIP     ${svc.spec.clusterIP}
    ${new_conf}=      Set To Dictionary     ${conf}     spec     ${new_spec}
    ${new_metadata}=     Create Dictionary     name=myservice     namespace=default     resourceVersion=${svc.metadata.resourceVersion}
    ${new_conf}=      Set To Dictionary     ${new_conf}     metadata     ${new_metadata}
    replace svc  ${new_conf}
    ${conf}=     read conf     testcases/dynamic_client/resources/svc_lookup.yaml
    create pod     ${conf}
    sleep     5 seconds
    KubeLibrary.wait pod completion      default      label_selector=app=svc-lookup
    [Teardown]      Run Keywords     delete pod     default     svc-lookup       AND         delete svc     default     myservice