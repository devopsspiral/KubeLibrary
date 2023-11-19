*** Settings ***
Resource      ./exec_kw.robot
Force Tags    exec    other

*** Variables ***
${string}            Hello
${CONTAINER_NAME}    grafana

*** Test Cases ***
Exec test case example
    ${command}    Create List    /bin/sh    -c    echo ${string}
    Set Pod Name For Namespace
    ${stdout}    Get Namespaced Pod Exec    name=${POD_NAME}
    ...                                     namespace=${namespace}
    ...                                     argv_cmd=${command}
    Should Be Equal    ${stdout}   ${string}
    ...    msg=Stdout should be ${string} not ${stdout}!

Exec multiple commands
    ${command}    Create List    /bin/sh    -c    echo 1 && echo 2 && echo 3
    Set Pod Name For Namespace
    ${stdout}    Get Namespaced Pod Exec    name=${POD_NAME}
    ...                                     namespace=${namespace}
    ...                                     argv_cmd=${command}
    Should Be Equal    ${stdout}   1\n2\n3
    ...    msg=Stdout should be ${string} not ${stdout}!

Exec command for specific container
    ${command}    Create List    /bin/sh    -c    echo ${string}
    Set Pod Name For Namespace
    ${stdout}    Get Namespaced Pod Exec    name=${POD_NAME}
    ...                                     namespace=${namespace}
    ...                                     argv_cmd=${command}
    ...                                     container=${CONTAINER_NAME}
    Should Be Equal    ${stdout}   ${string}
    ...    msg=Stdout should be ${string} not ${stdout}!

Exec wrong command syntax
    Set Pod Name For Namespace
    Run Keyword And Expect Error    STARTS: TypeError:
    ...    Get Namespaced Pod Exec    name=${POD_NAME}
    ...                               namespace=${namespace}
    ...                               argv_cmd=echo ${string}
