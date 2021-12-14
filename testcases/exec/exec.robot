*** Settings ***
Resource      ./exec_kw.robot
Force Tags    exec    other    prerelease

*** Variables ***
${string}    Hello

*** Test Cases ***
Exec test case example
    Set Pod Name For Namespace
    ${stdout}    Get Namespaced Pod Exec    name=${POD_NAME}
    ...                                     namespace=${namespace}
    ...                                     cmd=echo ${string}
    Should Be Equal    ${stdout}   ${string}
    ...    msg=Stdout should be ${string} not ${stdout}!
