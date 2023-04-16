import json
import re
import ssl
import urllib3

from os import environ
from kubernetes import client, config, dynamic, stream
from robot.api import logger
from robot.api.deco import library
from string import digits, ascii_lowercase
from random import choices

from KubeLibrary.exceptions import BearerTokenWithPrefixException
from KubeLibrary.version import version

# supressing SSL warnings when using self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DynamicClient(dynamic.DynamicClient):
    @property
    def api_client(self):
        return self.client


@library(scope="GLOBAL", version=version, auto_keywords=True)
class KubeLibrary:
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

        Environment variables:
        - INIT_FOR_LIBDOC_ONLY:
          Set to '1' to generate keyword documentation and skip to load a kube config..
        """
        if "1" == environ.get('INIT_FOR_LIBDOC_ONLY', "0"):
            return
        self.reload_config(kube_config=kube_config, context=context, api_url=api_url, bearer_token=bearer_token,
                           ca_cert=ca_cert, incluster=incluster, cert_validation=cert_validation)

    @staticmethod
    def get_proxy():
        return environ.get('https_proxy') or environ.get('HTTPS_PROXY') or environ.get('http_proxy') or environ.get('HTTP_PROXY')

    @staticmethod
    def get_no_proxy():
        return environ.get('no_proxy') or environ.get('NO_PROXY')

    @staticmethod
    def generate_alphanumeric_str(size):
        """Generates a random alphanumeric string with given size.

        Returns a string.

        - ``size``:
          Desired size of the output string
        """
        return "".join(choices(ascii_lowercase + digits, k=size))

    @staticmethod
    def evaluate_callable_from_k8s_client(attr_name, *args, **kwargs):
        """Evaluates a callable from kubernetes client.

        Returns the output of the client callable.

        - ``attr_name``:
          Callable name
        - ``*args``:
          Positional arguments for argument forwarding
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        attr = getattr(client, attr_name, None)
        assert callable(attr), f"kubernetes.client does not contain {attr_name}!"
        return attr(*args, **kwargs)

    def get_dynamic_resource(self, api_version, kind):
        """Returns a dynamic resource based on the provided api version and kind.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        """
        return self.dynamic.resources.get(api_version=api_version, kind=kind)

    def get(self, api_version, kind, **kwargs):
        """Retrieves resource instances based on the provided parameters.

        Can be optionally given a ``namespace``, ``name``, ``label_selector``, ``body`` and ``field_selector``.

        Returns a resource list.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        resource = self.get_dynamic_resource(api_version, kind)
        return resource.get(**kwargs)

    def create(self, api_version, kind, **kwargs):
        """Creates resource instances based on the provided configuration.

        If the resource is namespaced (ie, not cluster-level), then one of ``namespace``, ``label_selector``, or ``field_selector`` is required.
        If the resource is cluster-level, then one of ``name``, ``label_selector``, or ``field_selector`` is required.
        Can be optionally given a kubernetes manifest (``body``) which respects the above considerations.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        resource = self.get_dynamic_resource(api_version, kind)
        resource.create(**kwargs)

    def delete(self, api_version, kind, **kwargs):
        """Deletes resource instances based on the provided configuration.

        Can be optionally given a ``namespace``, ``name``, ``label_selector``, ``body`` and ``field_selector``.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        resource = self.get_dynamic_resource(api_version, kind)
        resource.delete(**kwargs)

    def patch(self, api_version, kind, **kwargs):
        """Patches resource instances based on the provided parameters.

        Can be optionally given a ``namespace``, ``name``, ``label_selector``, ``body`` and ``field_selector``.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        resource = self.get_dynamic_resource(api_version, kind)
        resource.patch(**kwargs)

    def replace(self, api_version, kind, **kwargs):
        """Replaces resource instances based on the provided parameters.

        Can be optionally given a ``namespace``, ``name``, ``label_selector``, ``body`` and ``field_selector``.

        - ``api_version``:
          Api version of the desired kubernetes resource
        - ``kind``:
          Kind of the desired kubernetes resource
        - ``**kwargs``:
          Keyword arguments for argument forwarding
        """
        resource = self.get_dynamic_resource(api_version, kind)
        resource.replace(**kwargs)

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

        Environment variables:
        - HTTP_PROXY:
          Proxy URL
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
            configuration._default.proxy = KubeLibrary.get_proxy()
            configuration._default.no_proxy = KubeLibrary.get_no_proxy()
            configuration.api_key["authorization"] = bearer_token
            configuration.api_key_prefix['authorization'] = 'Bearer'
            configuration.host = api_url
            configuration.ssl_ca_cert = ca_cert
            self.api_client = client.ApiClient(configuration)
        else:
            try:
                config.load_kube_config(kube_config, context)
                client.Configuration._default.proxy = KubeLibrary.get_proxy()
                client.Configuration._default.no_proxy = KubeLibrary.get_no_proxy()
            except TypeError:
                logger.error('Neither KUBECONFIG nor ~/.kube/config available.')

        if not self.api_client:
            self.api_client = client.ApiClient(configuration=client.Configuration().get_default_copy())

        self._add_api('v1', client.CoreV1Api)
        self._add_api('networkingv1api', client.NetworkingV1Api)
        self._add_api('batchv1', client.BatchV1Api)
        self._add_api('appsv1', client.AppsV1Api)
        # self._add_api('batchv1_beta1', client.BatchV1Api)
        self._add_api('custom_object', client.CustomObjectsApi)
        self._add_api('rbac_authv1_api', client.RbacAuthorizationV1Api)
        self._add_api('autoscalingv1', client.AutoscalingV1Api)
        self._add_api('dynamic', DynamicClient)

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

    def list_namespace(self, label_selector=""):
        """Lists available namespaces.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of namespaces.
        """
        ret = self.v1.list_namespace(watch=False, label_selector=label_selector)
        return ret.items

    def get_namespaces(self, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespace.
        Gets a list of available namespaces.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of namespaces names.
        """
        return self.filter_names(self.list_namespace(label_selector=label_selector))

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
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_pod_by_pattern.
        Gets pod name matching pattern in given namespace.

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

    def list_namespaced_pod_by_pattern(self, name_pattern, namespace, label_selector=""):
        """List pods matching pattern in given namespace.

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

    def get_pods_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_pod_by_pattern.
        Gets pods matching pattern in given namespace.

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

    def read_namespaced_pod_log(self, name, namespace, container):
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

    def get_pod_logs(self, name, namespace, container):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_pod_log.
        Gets container logs of given pod in given namespace.

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

    def list_namespaced_config_map_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Lists configmaps matching pattern in given namespace.

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

    def get_configmaps_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_config_map_by_pattern.
        Gets configmaps matching pattern in given namespace.

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

    def list_namespaced_service_account_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Lists service accounts matching pattern in given namespace.

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

    def get_service_accounts_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_service_account_by_pattern.
        Gets service accounts matching pattern in given namespace.

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

    def list_namespaced_deployment_by_pattern(self, name_pattern, namespace, label_selector=""):
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

    def get_deployments_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_deployment_by_pattern.
        Gets deployments matching pattern in given namespace.

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

    def list_namespaced_replica_set_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Lists replicasets matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of  replicasets.

        - ``name_pattern``:
          replicaset name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_replica_set(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        replicasets = [item for item in ret.items if r.match(item.metadata.name)]
        return replicasets

    def get_replicasets_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_replica_set_by_pattern.
        Gets replicasets matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of  replicasets.

        - ``name_pattern``:
          replicaset name pattern to check
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_replica_set(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        replicasets = [item for item in ret.items if r.match(item.metadata.name)]
        return replicasets

    def list_namespaced_job_by_pattern(self, name_pattern, namespace, label_selector=""):
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

    def get_jobs_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_job_by_pattern.
        Gets jobs matching pattern in given namespace.

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

    def list_namespaced_secret_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Lists secrets matching pattern in given namespace.

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

    def get_secrets_in_namespace(self, name_pattern, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_secret_by_pattern.
        Gets secrets matching pattern in given namespace.

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

    def get_namespaced_pod_exec(self, name, namespace, argv_cmd, container=None):
        """Exec command on selected container for POD.

        Returns command stdout/stderr

        - ``name``:
          pod name
        - ``namespace``:
          namespace to check
        - ``argv_cmd``:
          command to be executed using argv syntax: ["/bin/sh", "-c", "ls"]
          it do not use shell as default!
        - ``container``:
          container on which we run exec, default: None
        """
        if not isinstance(argv_cmd, list) or not len(argv_cmd):
            raise TypeError(
                f"argv_cmd parameter should be a list and contains values like [\"/bin/bash\", \"-c\", \"ls\"] "
                f"not {argv_cmd}")
        if not container:
            return stream.stream(self.v1.connect_get_namespaced_pod_exec,
                                 name,
                                 namespace,
                                 command=argv_cmd,
                                 stderr=True,
                                 stdin=True,
                                 stdout=True,
                                 tty=False).strip()
        else:
            return stream.stream(self.v1.connect_get_namespaced_pod_exec,
                                 name,
                                 namespace,
                                 container=container,
                                 command=argv_cmd,
                                 stderr=True,
                                 stdin=True,
                                 stdout=True,
                                 tty=False).strip()

    def filter_names(self, objects):
        """Filter .metadata.name for list of k8s objects.

        Returns list of strings.

        - ``objects``:
          List of k8s objects
        """
        return [obj.metadata.name for obj in objects]

    def filter_by_key(self, objects, key, match):
        """Filter object with key matching value for list of k8s objects.

        Returns list of objects.

        - ``objects``:
          List of k8s objects
        - ``key``:
          Key to match
        - ``match``:
          Value of the key based on which objects will be included
        """
        return [obj for obj in objects if getattr(obj, key) == match]

    def filter_deployments_names(self, deployments):
        """*DEPRECATED* Will be removed in v1.0.0. See examples in TBD.
        Returns list of strings.
        - ``deployments``:
          List of deployments objects
        """
        return self.filter_names(deployments)

    def filter_replicasets_names(self, replicasets):
        """*DEPRECATED* Will be removed in v1.0.0. See examples in TBD.
        Returns list of strings.
        - ``replicasets``:
          List of replicasets objects
        """
        return self.filter_names(replicasets)

    def filter_pods_names(self, pods):
        """*DEPRECATED* Will be removed in v1.0.0. See examples in TBD.
        Filter pod names for list of pods.

        Returns list of strings.

        - ``pods``:
          List of pods objects
        """
        return self.filter_names(pods)

    def filter_service_accounts_names(self, service_accounts):
        """*DEPRECATED* Will be removed in v1.0.0. See examples in TBD.
        Filter service accounts names for list of service accounts.

        Returns list of strings.

        - ``service_accounts``:
          List of service accounts objects
        """
        return self.filter_names(service_accounts)

    def filter_configmap_names(self, configmaps):
        """*DEPRECATED* Will be removed in v1.0.0. See examples in TBD.
        Filter configmap  names for list of configmaps.
        Returns list of strings.
        - ``configmaps``:
          List of configmap objects
        """
        return self.filter_names(configmaps)

    def filter_endpoints_names(self, endpoints):
        """Filter endpoints names for list of endpoints.
        Returns list of strings.
        - ``endpoints``:
        List of endpoint objects
        """
        return self.filter_names(endpoints.items)

    @staticmethod
    def filter_pods_containers_by_name(pods, name_pattern):
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

    @staticmethod
    def filter_containers_images(containers):
        """Filters container images for given lists of containers.

        Returns list of images.

        - ``containers``:
          List of containers
        """
        return [container.image for container in containers]

    @staticmethod
    def filter_containers_resources(containers):
        """Filters container resources for given lists of containers.

        Returns list of resources.

        - ``containers``:
          List of containers
        """
        return [container.resources for container in containers]

    @staticmethod
    def filter_pods_containers_statuses_by_name(pods, name_pattern):
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

    def read_namespaced_pod_status(self, name, namespace):
        """Reads pod status in given namespace.

        - ``name``:
          Name of pod.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_pod_status(name, namespace)
        return ret.status

    def get_pod_status_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_pod_status.

        - ``name``:
          Name of pod.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_pod_status(name, namespace)
        return ret.status.phase

    @staticmethod
    def assert_pod_has_labels(pod, labels_json):
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

    @staticmethod
    def assert_pod_has_annotations(pod, annotations_json):
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

    @staticmethod
    def assert_container_has_env_vars(container, env_vars_json):
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

    def list_namespaced_service(self, namespace, label_selector=""):
        """Gets services in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_service(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def get_services_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_service.

        Gets services in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_service(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_service(self, name, namespace):
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

    def get_service_details_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_service.

        Gets service details in given namespace.

        Returns Service object representation. Can be accessed using

        | Should Be Equal As integers    | ${service_details.spec.ports[0].port}    | 8080 |

        - ``name``:
          Name of service.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_service(name, namespace)
        return ret

    def list_namespaced_horizontal_pod_autoscaler(self, namespace, label_selector=""):
        """Gets Horizontal Pod Autoscalers in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.autoscalingv1.list_namespaced_horizontal_pod_autoscaler(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def get_hpas_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_horizontal_pod_autoscaler.

        Gets Horizontal Pod Autoscalers in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.autoscalingv1.list_namespaced_horizontal_pod_autoscaler(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_horizontal_pod_autoscaler(self, name, namespace):
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

    def get_hpa_details_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_horizontal_pod_autoscaler.

        Gets Horizontal Pod Autoscaler details in given namespace.

        Returns Horizontal Pod Autoscaler object representation. Can be accessed using

        | Should Be Equal As integers    | ${hpa_details.spec.target_cpu_utilization_percentage}    | 50 |

        - ``name``:
          Name of Horizontal Pod Autoscaler
        - ``namespace``:
          Namespace to check
        """
        ret = self.autoscalingv1.read_namespaced_horizontal_pod_autoscaler(name, namespace)
        return ret

    def read_namespaced_endpoints(self, name, namespace):
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

    def get_endpoints_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_endpoints.

        Gets endpoint details in given namespace.

        Returns Endpoint object representation. Can be accessed using

        | Should Match    | ${endpoint_details.subsets[0].addresses[0].target_ref.name}    | pod-name-123456 |

        - ``name``:
          Name of endpoint.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_endpoints(name, namespace)
        return ret

    def list_namespaced_persistent_volume_claim(self, namespace, label_selector=""):
        """Gets pvcs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_persistent_volume_claim(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def list_namespaced_persistent_volume_claim_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Gets pvcs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

       Returns list of strings.

        - ``namespace``:
          Namespace to check
        - ``name_pattern``:
          pvc name pattern to check
        """
        ret = self.v1.list_namespaced_persistent_volume_claim(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        return [item for item in ret.items if r.match(item.metadata.name)]

    def list_namespaced_stateful_set(self, namespace, label_selector=""):
        """Lists statefulsets in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of  statefulsets.

        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_stateful_set(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def list_namespaced_stateful_set_by_pattern(self, name_pattern, namespace, label_selector=""):
        """Lists statefulsets matching pattern in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of  statefulsets.

        - ``namespace``:
          Namespace to check
        - ``name_pattern``:
          statefulset name pattern to check
        """
        ret = self.appsv1.list_namespaced_stateful_set(namespace, watch=False, label_selector=label_selector)
        r = re.compile(name_pattern)
        statefulsets = [item for item in ret.items if r.match(item.metadata.name)]
        return statefulsets

    def get_pvc_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_persistent_volume_claim.

        Gets pvcs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_persistent_volume_claim(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_persistent_volume_claim(self, name, namespace):
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

    def get_pvc_capacity(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_persistent_volume_claim.

        Gets PVC details in given namespace.

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

    def create_namespaced_service_account(self, namespace, body):
        """Creates service account in a namespace

        Returns created service account

        - ``body``:
          Service Account object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.create_namespaced_service_account(namespace=namespace, body=body)
        return ret

    def create_service_account_in_namespace(self, namespace, body):
        """*DEPRECATED* Will be removed in v1.0.0. Use create_namespaced_service_account.

        Creates service account in a namespace

        Returns created service account

        - ``body``:
          Service Account object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.create_namespaced_service_account(namespace=namespace, body=body)
        return ret

    def delete_namespaced_service_account(self, name, namespace):
        """Deletes service account in a namespace

        Returns V1status


        - ``name``:
          Service Account name
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.delete_namespaced_service_account(name=name, namespace=namespace)
        return ret

    def delete_service_account_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use delete_namespaced_service_account.

        Deletes service account in a namespace

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

    def list_namespaced_ingress(self, namespace, label_selector=""):
        """Gets ingresses in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value
        Returns list of strings.
        - ``namespace``:
          Namespace to check
        """
        ret = self.networkingv1api.list_namespaced_ingress(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def get_ingresses_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_ingress.

        Gets ingresses in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value
        Returns list of strings.
        - ``namespace``:
          Namespace to check
        """
        ret = self.networkingv1api.list_namespaced_ingress(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_ingress(self, name, namespace):
        """Gets ingress details in given namespace.

        Returns Ingress object representation.
          Name of ingress.
        - ``namespace``:
          Namespace to check
        """
        ret = self.networkingv1api.read_namespaced_ingress(name, namespace)
        return ret

    def get_ingress_details_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_ingress.

        Gets ingress details in given namespace.

        Returns Ingress object representation.
          Name of ingress.
        - ``namespace``:
          Namespace to check
        """
        ret = self.networkingv1api.read_namespaced_ingress(name, namespace)
        return ret

    def list_namespaced_cron_job(self, namespace, label_selector=""):
        """Gets cron jobs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.list_namespaced_cron_job(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def get_cron_jobs_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_cron_job.

        Gets cron jobs in given namespace.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.list_namespaced_cron_job(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_cron_job(self, name, namespace):
        """Gets cron job details in given namespace.

        Returns Cron job object representation.

        - ``name``:
          Name of cron job.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.read_namespaced_cron_job(name, namespace)
        return ret

    def get_cron_job_details_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_cron_job.

        Gets cron job details in given namespace.

        Returns Cron job object representation.

        - ``name``:
          Name of cron job.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.read_namespaced_cron_job(name, namespace)
        return ret

    def list_namespaced_daemon_set(self, namespace, label_selector=""):
        """Gets a list of available daemonsets.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of deaemonsets.

        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_daemon_set(namespace, watch=False, label_selector=label_selector)
        return [item for item in ret.items]

    def get_daemonsets_in_namespace(self, namespace, label_selector=""):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_daemon_set.

        Gets a list of available daemonsets.

        Can be optionally filtered by label. e.g. label_selector=label_key=label_value

        Returns list of deaemonsets.

        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.list_namespaced_daemon_set(namespace, watch=False, label_selector=label_selector)
        return [item.metadata.name for item in ret.items]

    def read_namespaced_daemon_set(self, name, namespace):
        """Gets deamonset details in given namespace.

        Returns daemonset object representation.

        - ``name``:
          Name of the daemonset
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.read_namespaced_daemon_set(name, namespace)
        return ret

    def get_daemonset_details_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use read_namespaced_daemon_set.

        Gets deamonset details in given namespace.

        Returns daemonset object representation.

        - ``name``:
          Name of the daemonset
        - ``namespace``:
          Namespace to check
        """
        ret = self.appsv1.read_namespaced_daemon_set(name, namespace)
        return ret

    def list_cluster_role(self):
        """Gets a list of cluster_roles.

        Returns list of cluster_roles.
        """
        ret = self.rbac_authv1_api.list_cluster_role(watch=False)
        return [item for item in ret.items]

    def get_cluster_roles(self):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_cluster_role.

        Gets a list of cluster_roles.

        Returns list of cluster_roles.
        """
        ret = self.rbac_authv1_api.list_cluster_role(watch=False)
        return [item.metadata.name for item in ret.items]

    def list_cluster_role_binding(self):
        """Gets a list of cluster_role_bindings.

        Returns list of cluster_role_bindings.
        """
        ret = self.rbac_authv1_api.list_cluster_role_binding(watch=False)
        return [item for item in ret.items]

    def get_cluster_role_bindings(self):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_cluster_role_binding.

        Gets a list of cluster_role_bindings.

        Returns list of cluster_role_bindings.
        """
        ret = self.rbac_authv1_api.list_cluster_role_binding(watch=False)
        return [item.metadata.name for item in ret.items]

    def list_namespaced_role(self, namespace):
        """Gets roles in given namespace.

        Returns list of roles.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role(namespace, watch=False)
        return [item for item in ret.items]

    def get_roles_in_namespace(self, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_role.

        Gets roles in given namespace.

        Returns list of roles.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role(namespace, watch=False)
        return [item.metadata.name for item in ret.items]

    def list_namespaced_role_binding(self, namespace):
        """Gets role_bindings in given namespace.

        Returns list of role_bindings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role_binding(namespace, watch=False)
        return [item for item in ret.items]

    def get_role_bindings_in_namespace(self, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_namespaced_role_binding.

        Gets role_bindings in given namespace.

        Returns list of role_bindings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.rbac_authv1_api.list_namespaced_role_binding(namespace, watch=False)
        return [item.metadata.name for item in ret.items]

    def list_cluster_custom_object(self, group, version, plural):
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

    def list_cluster_custom_objects(self, group, version, plural):
        """*DEPRECATED* Will be removed in v1.0.0. Use list_cluster_custom_object.

        Lists cluster level custom objects.

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

    def get_namespaced_custom_object(self, group, version, namespace, plural, name):
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

    def get_custom_object_in_namespace(self, group, version, namespace, plural, name):
        """*DEPRECATED* Will be removed in v1.0.0. Use get_namespaced_custom_object.

        Get custom object in namespace.

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

    def create_namespaced_cron_job(self, namespace, body):
        """Creates cron_job in a namespace

        Returns created cron_job
        - ``body``:
          Cron_job object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.create_namespaced_cron_job(namespace=namespace, body=body)
        return ret

    def create_cron_job_in_namespace(self, namespace, body):
        """*DEPRECATED* Will be removed in v1.0.0. Use create_namespaced_cron_job.

        Creates cron_job in a namespace

        Returns created cron_job
        - ``body``:
          Cron_job object.
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.create_namespaced_cron_job(namespace=namespace, body=body)
        return ret

    def delete_namespaced_cron_job(self, name, namespace):
        """Deletes cron_job in a namespace

        Returns V1 status
        - ``name``:
          Cron Job name
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.delete_namespaced_cron_job(name=name, namespace=namespace)
        return ret

    def delete_cron_job_in_namespace(self, name, namespace):
        """*DEPRECATED* Will be removed in v1.0.0. Use delete_namespaced_cron_job.

        Deletes cron_job in a namespace

        Returns V1 status
        - ``name``:
          Cron Job name
        - ``namespace``:
          Namespace to check
        """
        ret = self.batchv1.delete_namespaced_cron_job(name=name, namespace=namespace)
        return ret
