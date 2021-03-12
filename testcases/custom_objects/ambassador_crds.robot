*** Settings ***
Library         KubeLibrary

Documentation  These are example test cases to check custom resource definitions created by Ambassador.
...            Ambassador is on open source API gateway solution. The most common CRDs created by ambassador 
...            are Mappings and Hosts, which control the routing of API requests to different services
...            running in your cluster.
...            https://www.getambassador.io/products/api-gateway/
...            More details on Ambassador Mappings:
...            https://www.getambassador.io/docs/pre-release/topics/using/intro-mappings/#introduction-to-the-mapping-resource

*** Test Cases ***
Get details for all ambassador mappings
    ${listed_mappings}=  List Cluster Custom Objects   getambassador.io   v2   mappings
    FOR  ${mapping}  IN  @{listed_mappings['items']}
        Log  Mapping name: ${mapping}[metadata][name]  console=True
        Log  Mapping namespace: ${mapping}[metadata][namespace]  console=True
        Log  Mapping prefix: ${mapping}[spec][prefix]  console=True
        Log  Mapping service: ${mapping}[spec][service]  console=True
        ${status}=  Run Keyword And Ignore Error  Log  Mapping status: ${mapping}[status][state]  console=True
        Run Keyword If   '''FAIL''' in '''${status}'''  Log  ! Mapping ${mapping}[metadata][name] is not running  console=True
        Log  ---------------------------------------------------  console=True
    END

Get details for all ambassador hosts
    ${listed_hosts}=  List Cluster Custom Objects   getambassador.io   v2   hosts
    FOR  ${host}  IN  @{listed_hosts['items']}
        Log  Host name: ${host}[metadata][name]  console=True
        Log  Host namespace: ${host}[metadata][namespace]  console=True
        Log  Host hostname: ${host}[spec][hostname]  console=True
        Log  Host status: ${host}[status][state]  console=True
        Log  ---------------------------------------------------  console=True
    END
