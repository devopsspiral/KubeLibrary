*** Settings ***
Library    OperatingSystem

Documentation    To have a valid kube_config file for a Google Cloud hosted GKE cluster, 
...              you need to run "gcloud auth activate-service-account". 
...              gcloud saves an access token with expiration time in your kube_config file.
...              By running "gcloud auth activate-service-account" this token gets renewed.

*** Keywords ***
Connect to GKE cluster
    Run    gcloud auth activate-service-account ${GCLOUD_SERVICE_ACCOUNT} --key-file=${GCLOUD_SA_CREDENTIALS_FILE}
    Import Library    KubeLibrary    kube_config=${kube_config}
