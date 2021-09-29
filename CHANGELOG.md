# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## In progress
### Added
- Keyword for getting Horizontal Pod Autoscalers [#80](https://github.com/devopsspiral/KubeLibrary/pull/80 )by [@Nilsty](https://github.com/Nilsty)
- Keyword for list cluster role and cluster role binding [#58](https://github.com/devopsspiral/KubeLibrary/pull/58) by [@satish-nubolab](https://github.com/satish-nubolab)
- Keyword for getiing role and rolebinding [#56](https://github.com/devopsspiral/KubeLibrary/pull/56) by [@satish-nubolab](https://github.com/satish-nubolab)
- Bearer token authentication [#39](https://github.com/devopsspiral/KubeLibrary/pull/39) by [@m-wcislo](https://github.com/m-wcislo)
- Keyoword for create and delete a cronjob [#71](https://github.com/devopsspiral/KubeLibrary/pull/71) by [@satish-nubolab](https://github.com/satish-nubolab)
- Keywords for get replicaset in a namespace [#82](https://github.com/devopsspiral/KubeLibrary/pull/92) by [@hello2ray](https://github.com/hello2ray)
## [0.4.0] - 2021-03-12
### Added
- Kubeconfig context support [#36](https://github.com/devopsspiral/KubeLibrary/pull/36) by [@m-wcislo](https://github.com/m-wcislo)
- Keyword for getting secrets [#31](https://github.com/devopsspiral/KubeLibrary/pull/31 )by [@Nilsty](https://github.com/Nilsty)
- Keyword for cluster healthcheck [#40](https://github.com/devopsspiral/KubeLibrary/pull/40) by [@satish-nubolab](https://github.com/satish-nubolab)
- Extend cluster healthcheck [#47](https://github.com/devopsspiral/KubeLibrary/pull/47) by [@mika-b](https://github.com/mika-b)
- Keyword for list ingress [#38](https://github.com/devopsspiral/KubeLibrary/pull/38) by [@satish-nubolab](https://github.com/satish-nubolab)
- Keyword for list cronjob [#48](https://github.com/devopsspiral/KubeLibrary/pull/48) by [@satish-nubolab](https://github.com/satish-nubolab)
- Keyword for list daemonset [#50](https://github.com/devopsspiral/KubeLibrary/pull/50) by [@satish-nubolab](https://github.com/satish-nubolab)
- Keyword for CustomObjectsApi [#54](https://github.com/devopsspiral/KubeLibrary/pull/54) by [@mika-b](https://github.com/mika-b)
- Example tests for Ambassador CRDs [#63](https://github.com/devopsspiral/KubeLibrary/pull/63) by [@Nilsty](https://github.com/Nilsty)
- Example tests for Ambassador CRDs [#63](https://github.com/devopsspiral/KubeLibrary/pull/63) by [@Nilsty](https://github.com/Nilsty)
- Keyword for edit ,create and delete ingress [#52]((https://github.com/devopsspiral/KubeLibrary/pull/94) by [@satish-nubolab](https://github.com/satish-nubolab)

### Fixed
- Fix for cert validation disabling not being possible for all api clients [#61](https://github.com/devopsspiral/KubeLibrary/pull/61) by [@m-wcislo](https://github.com/m-wcislo)

### Fixed
- cert_validation=False was not affecting all used APIs
## [0.3.0] - 2021-02-01

### Added
- CI implementation [#14](https://github.com/devopsspiral/KubeLibrary/pull/14) by [@m-wcislo](https://github.com/m-wcislo)
- keywords to list deployments [#13](https://github.com/devopsspiral/KubeLibrary/pull/13) by [@Nilsty](https://github.com/Nilsty)
- keywords for get/create/delete service accounts [#28](https://github.com/devopsspiral/KubeLibrary/pull/28) by [@kutayy](https://github.com/kutayy)   


## [0.2.0] - 2020-09-03

### Added
- Update docs with latest libdoc version [#11](https://github.com/devopsspiral/KubeLibrary/pull/11) by [@Nilsty](https://github.com/Nilsty)
- Example test case to connect to a GKE cluster [#10](https://github.com/devopsspiral/KubeLibrary/pull/10) by [@Nilsty](https://github.com/Nilsty)
- Adding label selectors [#9](https://github.com/devopsspiral/KubeLibrary/pull/9) by [@Nilsty](https://github.com/Nilsty)
- Adding keyword to Reload the configuration of the KubeLibrary [#8](https://github.com/devopsspiral/KubeLibrary/pull/8) by [@Nilsty](https://github.com/Nilsty)
- Adding keyword and tests for "Get Pod Logs" [#7](https://github.com/devopsspiral/KubeLibrary/pull/7) by [@Nilsty](https://github.com/Nilsty)
- Adding keyword to read jobs [#6](https://github.com/devopsspiral/KubeLibrary/pull/6) by [@Nilsty](https://github.com/Nilsty)


## [0.1.4] - 2020-07-28
 
### Added
- pod generic testcases added, should be extended in future
- add kw for getting configmaps, update docs [#5](https://github.com/devopsspiral/KubeLibrary/pull/5) by [@Nilsty](https://github.com/Nilsty)
 
### Changed
- reorganized library functions to getters, filters and asserts
- python unit tests
