import json
import re
import ssl
import urllib3
from kubernetes import client, config, dynamic
from robot.api import logger
from string import digits, ascii_lowercase
from random import choices
from backoff import on_predicate, constant

# supressing SSL warnings when using self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BearerTokenWithPrefixException(Exception):

    ROBOT_SUPPRESS_NAME = True

    def __init__(self):
        super().__init__("Unnecessary 'Bearer ' prefix in token")
    pass


class KubeLibrary(object):
    """KubeLibrary is a Robot Framework test library for Kubernetes.

    The approach taken by this library is to provide easy to access kubernetes objects representation that can
    be then accessed to define highlevel keywords for tests.

    = Kubeconfigs =

    By default ~/.kube/config is used. Kubeconfig location
    can also be passed by setting KUBECONFIG environment variable or as Library argument.

    | ***** Settings *****
    | Library           KubeLibrary          /path/to/kubeconfig

    = Context =

    By default current context from kubeconfig is used. Setting multiple contexts in
    different test suites allows working on multiple clusters.

    | ***** Settings *****
    | Library           KubeLibrary          context=k3d-k3d-cluster2

    = Bearer token authentication =

    It is possible to authenticate using bearer token by passing API url, bearer token and optionally CA certificate.

    | ***** Settings *****
    | Library           KubeLibrary          api_url=%{K8S_API_URL}    bearer_token=%{K8S_TOKEN}    ca_cert=%{K8S_CA_CRT}

    = In cluster execution =

    If tests are supposed to be executed from within cluster, KubeLibrary can be configured to use standard
    token authentication. Just set incluster parameter to True.

    = Auth methods precedence =

    If enabled, auth methods takes precedence in following order:
    1. Incluster
    2. Bearer Token
    3. Kubeconfig

    | ***** Settings *****
    | Library           KubeLibrary          None    True

    """
    def __init__(self, kube_config=None, context=None, api_url=None, bearer_token=None,
                 ca_cert=None, incluster=False, cert_validation=True):
        """KubeLibrary can be configured with several optional arguments.
        - ``kube_config``:
          Path pointing to kubeconfig of target Kubernetes cluster.
        - ``context``:
          Active context. If None current_context from kubeconfig is used.
        - ``api_url``:
          K8s API url, used for bearer token authenticaiton.
        - ``bearer_token``:
          Bearer token, used for bearer token authenticaiton. Do not include 'Bearer ' prefix.
        - ``ca_cert``:
          Optional CA certificate file path, used for bearer token authenticaiton.
        - ``incuster``:
          Default False. Indicates if used from within k8s cluster. Overrides kubeconfig.
        - ``cert_validation``:
          Default True. Can be set to False for self-signed certificates.
        """
        self.reload_config(kube_config=kube_config, context=context, api_url=api_url, bearer_token=bearer_token,
                           ca_cert=ca_cert, incluster=incluster, cert_validation=cert_validation)

    @property
    def api_client(self):
        return self.api_client

    @property
    def dynamic_client(self):
      return self.dynamic_client

    @staticmethod
    def get_names_from_resource_list(resource_list):
        return {item.metadata.name for item in resource_list.items}

    @staticmethod
    def generate_random_name(size):
        return "".join(choices(ascii_lowercase + digits, k=size))

    @staticmethod
    def get_from_k8s_client(attr_name, *args, **kwargs):
        attr = getattr(client, attr_name, None)
        assert callable(attr), f"kubernetes.client does not contain {attr_name}!"
        return attr(*args, **kwargs)

    def get(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        return resource.get(**kwargs)

    def create(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        resource.create(**kwargs)

    def delete(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        resource.delete(**kwargs)

    def patch(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        resource.patch(**kwargs)

    def replace(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        resource.replace(**kwargs)

    def watch(self, api_version, kind, **kwargs):
        resource = self.dynamic_client.resources.get(api_version=api_version, kind=kind)
        yield resource.watch(**kwargs)

    @on_predicate(constant, lambda x: x not in ("succeeded", "failed", "unknown"), interval=5, max_time=60)
    def wait_pod_completion(self, label_selector="", namespace=None):
        namespace = self.resolve_namespace(namespace)
        pod_list = self.get(kind="Pod", api_version="v1", namespace=namespace, label_selector=label_selector)
        assert len(pod_list.items) > 0, f"Found no pods in {namespace} with label selector {label_selector}!"
        return pod_list.items[0].status.phase.lower()

    def reload_config(self, kube_config=None, context=None, api_url=None, bearer_token=None, ca_cert=None, incluster=False, cert_validation=True):
        """Reload the KubeLibrary to be configured with different optional arguments.
           This can be used to connect to a different cluster during the same test.
        - ``kube_config``:
          Path pointing to kubeconfig of target Kubernetes cluster.
        - ``context``:
          Active context. If None current_context from kubeconfig is used.
        - ``api_url``:
          K8s API url, used for bearer token authenticaiton.
        - ``bearer_token``:
          Bearer token, used for bearer token authenticaiton. Do not include 'Bearer ' prefix.
        - ``ca_cert``:
          Optional CA certificate file path, used for bearer token authenticaiton.
        - ``incuster``:
          Default False. Indicates if used from within k8s cluster. Overrides kubeconfig.
        - ``cert_validation``:
          Default True. Can be set to False for self-signed certificates.
        """
        self.api_client = None
        self.cert_validation = cert_validation
        if incluster:
            try:
                config.load_incluster_config()
            except config.config_exception.ConfigException as e:
                logger.error('Are you sure tests are executed from within k8s cluster?')
                raise e
        elif api_url and bearer_token:
            if bearer_token.startswith('Bearer '):
                raise BearerTokenWithPrefixException
            configuration = client.Configuration()
            configuration.api_key["authorization"] = bearer_token
            configuration.api_key_prefix['authorization'] = 'Bearer'
            configuration.host = api_url
            configuration.ssl_ca_cert = ca_cert
            self.api_client = client.ApiClient(configuration)
        else:
            try:
                config.load_kube_config(kube_config, context)
            except TypeError:
                logger.error('Neither KUBECONFIG nor ~/.kube/config available.')
        self._add_api('v1', client.CoreV1Api)
        self._add_api('extensionsv1beta1', client.ExtensionsV1beta1Api)
        self._add_api('batchv1', client.BatchV1Api)
        self._add_api('appsv1', client.AppsV1Api)
        self._add_api('batchv1_beta1', client.BatchV1beta1Api)
        self._add_api('custom_object', client.CustomObjectsApi)
        self._add_api('rbac_authv1_api', client.RbacAuthorizationV1Api)
        self._add_api('autoscalingv1', client.AutoscalingV1Api)
        self.dynamic_client = dynamic.DynamicClient(self.api_client)

    def _add_api(self, reference, class_name):
        self.__dict__[reference] = class_name(self.api_client)
        if not self.cert_validation:
            self.__dict__[reference].api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'] = ssl.CERT_NONE

    def k8s_api_ping(self):
        """Performs GET on /api/v1/ for simple check of API availability.

        Returns tuple of (response data, response status, response headers). Can be used as prerequisite in tests.
        """
        path_params = {}
        query_params = []
        header_params = {}
        auth_settings = ['BearerToken']
        resp = self.v1.api_client.call_api('/api/v1/', 'GET',
                                           path_params,
                                           query_params,
                                           header_params,
                                           response_type='str',
                                           auth_settings=auth_settings,
                                           async_req=False,
                                           _return_http_data_only=False)
        return resp

    def get_namespaces(self, label_selector=""):
        """Gets a list of available namespaces.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of namespaces.
        """
        ret = self.v1.list_namespace(watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_healthy_nodes_count(self, label_selector=""):
        """Counts node with KubeletReady and status True.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Can be used to check number of healthy nodes. Can be used as prerequisite in tests.
        """
        ret = self.v1.list_node(watch=False, label_selector=label_selector)
        healthy_nods = []
        for item in ret.items:
            for condition in item.status.conditions:
                if condition.reason == 'KubeletReady' and condition.status == 'True':
                    healthy_nods.append(item.metadata.name)
        return len(healthy_nods)

    def get_pod_names_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets pod name matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``name_pattern``:
          Pod name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_pod(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern + '.*')
        return [item.metadata.name for item in ret.items if r.match(item.metadata.name)]

    def get_pods_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets pods matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of pods.

        - ``name_pattern``:
          Pod name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_pod(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        pods = [item for item in ret.items if r.match(item.metadata.name)]
        return pods

    def get_pod_logs(self, name, namespace, container):
        """Gets container logs of given pod in given namespace.

        Returns logs.

        - ``name``:
          Pod name to check
        - ``namespace``:
          Namespace to check
        - ``container``:
          Container to check
        """
        pod_logs = self.v1.read_namespaced_pod_log(name=name, namespace=namespace, container=container, follow=False)
        return pod_logs

    def get_configmaps_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets configmaps matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of configmaps.

        - ``name_pattern``:
          configmap name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_config_map(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        configmaps = [item for item in ret.items if r.match(item.metadata.name)]
        return configmaps

    def get_service_accounts_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets service accounts matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of service accounts.

        - ``name_pattern``:
          Service Account name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_service_account(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        service_accounts = [item for item in ret.items if r.match(item.metadata.name)]
        return service_accounts

    def get_deployments_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets deployments matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of deployments.

        - ``name_pattern``:
          deployment name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_deployment(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        deployments = [item for item in ret.items if r.match(item.metadata.name)]
        return deployments

    def get_jobs_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets jobs matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of jobs.

        - ``name_pattern``:
          job name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.list_namespaced_job(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        jobs = [item for item in ret.items if r.match(item.metadata.name)]
        return jobs

    def get_secrets_in_namespace(self, name_pattern, namespace, label_selector=""):
        """Gets secrets matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of secrets.

        - ``name_pattern``:
          secret name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_secret(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        secrets = [item for item in ret.items if r.match(item.metadata.name)]
        return secrets

    def filter_deployments_names(self, deployments):
        """Filter deployment  names for list of deployments .
        Returns list of strings.
        - ``deployments``:
          List of deployments objects
        """
        return [d.metadata.name for d in deployments]

    def filter_pods_names(self, pods):
        """Filter pod names for list of pods.

        Returns list of strings.

        - ``pods``:
          List of pods objects
        """
        return [pod.metadata.name for pod in pods]

    def filter_service_accounts_names(self, service_accounts):
        """Filter service accounts names for list of service accounts.

        Returns list of strings.

        - ``service_accounts``:
          List of service accounts objects
        """
        return [sa.metadata.name for sa in service_accounts]

    def filter_pods_containers_by_name(self, pods, name_pattern):
        """Filters pods containers by name for given list of pods.

        Returns lists of containers (flattens).

        - ``pods``:
          List of pods objects
        """
        containers = []
        r = re.compile(name_pattern)
        for pod in pods:
            for container in pod.spec.containers:
                if r.match(container.name):
                    containers.append(container)
        return containers

    def filter_configmap_names(self, configmaps):
        """Filter configmap  names for list of configmaps.
        Returns list of strings.
        - ``configmaps``:
          List of configmap objects
        """
        return [c.metadata.name for c in configmaps]

    def filter_containers_images(self, containers):
        """Filters container images for given lists of containers.

        Returns list of images.

        - ``containers``:
          List of containers
        """
        return [container.image for container in containers]

    def filter_containers_resources(self, containers):
        """Filters container resources for given lists of containers.

        Returns list of resources.

        - ``containers``:
          List of containers
        """
        return [container.resources for container in containers]

    def filter_pods_containers_statuses_by_name(self, pods, name_pattern):
        """Filters pods containers statuses by container name for given list of pods.

        Returns lists of containers statuses.

        - ``pods``:
          List of pods objects
        """
        container_statuses = []
        r = re.compile(name_pattern)
        for pod in pods:
            for container_status in pod.status.container_statuses:
                if r.match(container_status.name):
                    container_statuses.append(container_status)
        return container_statuses

    def get_pod_status_in_namespace(self, name, namespace):
        """Gets pod status in given namespace.

        - ``name``:
          Name of pod.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_pod_status(name, namespace)
        return ret.status.phase

    def assert_pod_has_labels(self, pod, labels_json):
        """Assert pod has labels.

        Returns True/False

        - ``pod``:
          Pod object.
        - ``labels_json``:
          JSON representing labels
        """
        try:
            labels = json.loads(labels_json)
            for k, v in labels.items():
                if pod.metadata.labels and k in pod.metadata.labels:
                    if pod.metadata.labels[k] != v:
                        logger.error(f'Label "{k}" value "{v}" not matching actual "{pod.metadata.labels[k]}"')
                        return False
                else:
                    logger.error(f'Label "{k}" not found in actual')
                    return False
            return True
        except json.JSONDecodeError:
            logger.error(f'Failed parsing Pod Labels JSON:{labels_json}')
            return False

    def assert_pod_has_annotations(self, pod, annotations_json):
        """Assert pod has annotations.

        Returns True/False

        - ``pod``:
          Pod object.
        - ``annotations_json``:
          JSON representing annotations
        """
        try:
            annotations = json.loads(annotations_json)
            for k, v in annotations.items():
                if pod.metadata.annotations and k in pod.metadata.annotations:
                    if pod.metadata.annotations[k] != v:
                        logger.error(f'Annotation "{k}" value "{v}" not matching actual "{pod.metadata.annotations[k]}"')
                        return False
                else:
                    logger.error(f'Annotation "{k}" not found in actual')
                    return False
            return True
        except json.JSONDecodeError:
            logger.error(f'Failed parsing Pod Annotations JSON:{annotations_json}')
            return False

    def assert_container_has_env_vars(self, container, env_vars_json):
        """Assert container has env vars.

        Returns True/False

        - ``container``:
          Container object.
        - ``env_var_json``:
          JSON representing env vars i.e.: {"EXAMPLE_VAR": "examplevalue"}
        """
        try:
            env_vars = json.loads(env_vars_json)
            for k, v in env_vars.items():
                found = False
                for ev in container.env:
                    if k == ev.name and v == ev.value:
                        found = True
                        break
                    elif k == ev.name and v != ev.value:
                        logger.error(f'Env var "{k}" value "{v}" not matching actual "{ev.value}"')
                        return False
                if not found:
                    logger.error(f'Env var "{k}" not found in actual')
                    return False
            return True
        except json.JSONDecodeError:
            logger.error(f'Failed parsing Container Env Var JSON:{env_vars_json}')
            return False

    def get_services_in_namespace(self, namespace, label_selector=""):
        """Gets services in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_service(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_service_details_in_namespace(self, name, namespace):
        """Gets service details in given namespace.

        Returns Service object representation. Can be accessed using

        | Should Be Equal As integers    | ${service_details.spec.ports[0].port}    | 8080 |

        - ``name``:
          Name of service.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_service(name, namespace)
        return ret

    def get_hpas_in_namespace(self, namespace, label_selector=""):
        """Gets Horizontal Pod Autoscalers in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.autoscalingv1.list_namespaced_horizontal_pod_autoscaler(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_hpa_details_in_namespace(self, name, namespace):
        """Gets Horizontal Pod Autoscaler details in given namespace.

        Returns Horizontal Pod Autoscaler object representation. Can be accessed using

        | Should Be Equal As integers    | ${hpa_details.spec.target_cpu_utilization_percentage}    | 50 |

        - ``name``:
          Name of Horizontal Pod Autoscaler
        - ``namespace``:
          Namespace to check
        """
        ret = self.autoscalingv1.read_namespaced_horizontal_pod_autoscaler(name, namespace)
        return ret

    def get_endpoints_in_namespace(self, name, namespace):
        """Gets endpoint details in given namespace.

        Returns Endpoint object representation. Can be accessed using

        | Should Match    | ${endpoint_details.subsets[0].addresses[0].target_ref.name}    | pod-name-123456 |

        - ``name``:
          Name of endpoint.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_endpoints(name, namespace)
        return ret

    def get_pvc_in_namespace(self, namespace, label_selector=""):
        """Gets pvcs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_persistent_volume_claim(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_pvc_capacity(self, name, namespace):
        """Gets PVC details in given namespace.

        Returns PVC object representation. Can be accessed using

        | Should Be Equal As strings    | ${pvc.status.capacity.storage}    | 1Gi |

        - ``name``:
          Name of PVC.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_persistent_volume_claim(name, namespace)
        return ret

    def get_kubelet_version(self, label_selector=""):
        """Gets list of kubelet versions on each node.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.
        """
        ret = self.v1.list_node(watch=False, label_selector=label_selector)
        return [item.status.node_info.kubelet_version for item in ret.items]

    def create_service_account_in_namespace(self, namespace, body):
        """Creates service account in a namespace

        Returns created service account

        - ``body``:
          Service Account object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.create_namespaced_service_account(namespace=namespace, body=body)
        return ret

    def delete_service_account_in_namespace(self, name, namespace):
        """Deletes service account in a namespace

        Returns V1status


        - ``name``:
          Service Account name
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.delete_namespaced_service_account(name=name, namespace=namespace)
        return ret

    def get_healthcheck(self, endpoint='/readyz', verbose=False):
        """Performs GET on /readyz or /livez for simple health check.

        Can be used to verify the readiness/current status of the API server
        Returns tuple of (response data, response status and response headers)

        - ``endpoint``:
            /readyz, /livez or induvidual endpoints like '/livez/etcd'. defaults to /readyz
        - ``verbose``:
            More detailed output.

        https://kubernetes.io/docs/reference/using-api/health-checks

        """
        path_params = {}
        query_params = []
        header_params = {}
        auth_settings = ['BearerToken']
        if not (endpoint.startswith('/readyz') or endpoint.startswith('/livez')):
            raise RuntimeError(f'{endpoint} does not start with "/readyz" or "/livez"')
        endpoint = endpoint if not verbose else endpoint + '?verbose'
        resp = self.v1.api_client.call_api(endpoint, 'GET',
                                           path_params,
                                           query_params,
                                           header_params,
                                           response_type='str',
                                           auth_settings=auth_settings,
                                           async_req=False,
                                           _return_http_data_only=False)
        return resp

    def get_ingresses_in_namespace(self, namespace, label_selector=""):
        """Gets ingresses in given namespace.
        Can be optionally filtered by label. e.g. label_selector=label_key=label_value
        Returns list of strings.
        - ``namespace``:
          Namespace to check
        """
        ret = self.extensionsv1beta1.list_namespaced_ingress(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_ingress_details_in_namespace(self, name, namespace):
        """Gets ingress details in given namespace.
        Returns Ingress object representation.
          Name of ingress.
        - ``namespace``:
          Namespace to check
        """
        ret = self.extensionsv1beta1.read_namespaced_ingress(name, namespace)
        return ret

    def get_cron_jobs_in_namespace(self, namespace, label_selector=""):
        """Gets cron jobs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1_beta1.list_namespaced_cron_job(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_cron_job_details_in_namespace(self, name, namespace):
        """Gets cron job details in given namespace.

        Returns Cron job object representation.

        - ``name``:
          Name of cron job.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1_beta1.read_namespaced_cron_job(name, namespace)
        return ret

    def get_daemonsets_in_namespace(self, namespace, label_selector=""):
        """Gets a list of available daemonsets.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of deaemonsets.

        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_daemon_set(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def get_daemonset_details_in_namespace(self, name, namespace):
        """Gets deamonset details in given namespace.

        Returns daemonset object representation.

        - ``name``:
          Name of the daemonset
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.read_namespaced_daemon_set(name, namespace)
        return ret

    def get_cluster_roles(self):
        """Gets a list of cluster_roles.

        Returns list of cluster_roles.
        """
        ret = self.rbac_authv1_api.list_cluster_role(watch=False)
        return [item.metadata.name for item in ret.items]

    def get_cluster_role_bindings(self):
        """Gets a list of cluster_role_bindings.

        Returns list of cluster_role_bindings.
        """
        ret = self.rbac_authv1_api.list_cluster_role_binding(watch=False)
        return [item.metadata.name for item in ret.items]

    def get_roles_in_namespace(self, namespace):
        """Gets roles in given namespace.

        Returns list of roles.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role(namespace, watch=False)
        return [item.metadata.name for item in ret.items]

    def get_role_bindings_in_namespace(self, namespace):
        """Gets role_bindings in given namespace.

        Returns list of role_bindings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role_binding(namespace, watch=False)
        return [item.metadata.name for item in ret.items]

    def list_cluster_custom_objects(self, group, version, plural):
        """Lists cluster level custom objects.

        Returns an object.

        - ``group``:
          API Group, e.g. 'k8s.cni.cncf.io'
        - ``version``:
          API version, e.g. 'v1'
        - ``plural``:
          e.g. 'network-attachment-definitions'

        As in ``GET /apis/{group}/{version}/{plural}``

        https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md
        """
        return self.custom_object.list_cluster_custom_object(group, version, plural)

    def get_cluster_custom_object(self, group, version, plural, name):
        """Get cluster level custom object.

        Returns an object.

        - ``group``:
          API Group, e.g. 'scheduling.k8s.io'
        - ``version``:
          API version, e.g. 'v1'
        - ``plural``:
          e.g. 'priorityclasses'
        - ``name``:
          e.g. 'system-node-critical'

        As in ``GET /apis/{group}/{version}/{plural}/{name}``

        https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md
        """
        return self.custom_object.get_cluster_custom_object(group, version, plural, name)

    def get_custom_object_in_namespace(self, group, version, namespace, plural, name):
        """Get custom object in namespace.

        Returns an object.

        - ``group``:
          API Group, e.g. 'k8s.cni.cncf.io'
        - ``version``:
          API version, e.g. 'v1'
        - ``namespace``:
          Namespace, e.g. 'default'
        - ``plural``:
          e.g. 'network-attachment-definitions'
        - ``name``:
          e.g. 'my-network'

        As in ``GET /apis/{group}/{version}/namespaces/{namespace}/{plural}/{name}``

        https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md
        """
        return self.custom_object.get_namespaced_custom_object(group, version, namespace, plural, name)

    def create_cron_job_in_namespace(self, namespace, body):
        """Creates cron_job in a namespace
        Returns created cron_job
        - ``body``:
          Cron_job object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1_beta1.create_namespaced_cron_job(namespace=namespace, body=body)
        return ret

    def delete_cron_job_in_namespace(self, name, namespace):
        """Deletes cron_job in a namespace
        Returns V1 status
        - ``name``:
          Cron Job name
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1_beta1.delete_namespaced_cron_job(name=name, namespace=namespace)
        return ret

    def filter_endpoints_names(self, endpoints):
        """Filter endpoints names for list of endpoints.
        Returns list of strings.
        - ``endpoints``:
        List of endpoint objects
        """
        return [endpoints.metadata.name for endpoints in endpoints.items]
