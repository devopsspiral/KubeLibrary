# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## In progress

## [0.8.0] - 2022-10-27
### Added
- Add function list_namespaced_stateful_set_by_pattern [#114](https://github.com/devopsspiral/KubeLibrary/pull/113) by [@siaomingjeng](https://github.com/siaomingjeng)
- Add function list_namespaced_persistent_volume_claim_by_pattern [#112](https://github.com/devopsspiral/KubeLibrary/pull/112) by [@siaomingjeng](https://github.com/siaomingjeng)

### Changed
- batchv1_beta1 deprecated
- ci uses latest default k8s and latest k3s
- octopus test helm chart removed as not working
## [0.7.0] - 2022-04-01
### Added
- Added keyword for handling kubectl exec [#102](https://github.com/devopsspiral/KubeLibrary/pull/101) by [@MarcinMaciaszek](https://github.com/MarcinMaciaszek)
### Changed
- networkingv1api used instead of extensionsv1beta1
## [0.6.2] - 2022-02-25

### Fixed
- Fix the kubernetes lib version (21.7.0) to still support extension/v1beta1 (ingress)

## [0.6.1] - 2022-01-27
### Changed
- Refactored setup.py & requirements, moved library scope to GLOBAL, sperated exceptions [#101](https://github.com/devopsspiral/KubeLibrary/pull/101) by [@MarcinMaciaszek](https://github.com/MarcinMaciaszek)

### Fixed
- Generate keyword documentation without a kubernetes cluster [#103](https://github.com/devopsspiral/KubeLibrary/pull/103) by [bli74](https://github.com/bli74)
## [0.6.0] - 2021-11-30
### Changed
- Helpers and keywords unification [#75](https://github.com/devopsspiral/KubeLibrary/pull/75) by [@m-wcislo](https://github.com/m-wcislo)
## [0.5.0] - 2021-10-03
### Added
- Dynamic client support and some utilities [#93](https://github.com/devopsspiral/KubeLibrary/pull/93) by [@mertkayhan](https://github.com/mertkayhan)
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
