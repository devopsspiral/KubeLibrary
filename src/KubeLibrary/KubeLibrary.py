import json
import re
import ssl
import urllib3
from kubernetes import client, config
from robot.api import logger

# supressing SSL warnings when using self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KubeLibrary(object):
    """KubeLibrary is a Robot Framework test library for Kubernetes.

    The approach taken by this library is to provide easy to access kubernetes objects representation that can 
    be then accessed to define highlevel keywords for tests.

    = Kubeconfigs =

    By default ~/.kube/config is used. Kubeconfig location
    can also be passed by setting KUBECONFIG environment variable or as Library argument.

    | ***** Settings *****
    | Library           KubeLibrary          /path/to/kubeconfig

    = In cluster execution =

    If tests are supposed to be executed from within cluster, KubeLibrary can be configured to use standard
    token authentication. Just set incluster parameter to True. If True then kubeconfigs are not used, 
    even if provided.

    | ***** Settings *****
    | Library           KubeLibrary          None    True

    """
    def __init__(self, kube_config=None, incluster=False, cert_validation=True):
        """KubeLibrary can be configured with several optional arguments.
        - ``kube_config``:
          Path pointing to kubeconfig of target Kubernetes cluster.
        - ``incuster``:
          Default False. Indicates if used from within k8s cluster. Overrides kubeconfig.
        - ``cert_validation``:
          Default True. Can be set to False for self-signed certificates.
        """
        self.reload_config(kube_config=kube_config, incluster=incluster, cert_validation=cert_validation)
    
    def reload_config(self, kube_config=None, incluster=False, cert_validation=True):
        """Reload the KubeLibrary to be configured with different optional arguments.
           This can be used to connect to a different cluster during the same test.
        - ``kube_config``:
          Path pointing to kubeconfig of target Kubernetes cluster.
        - ``incuster``:
          Default False. Indicates if used from within k8s cluster. Overrides kubeconfig.
        - ``cert_validation``:
          Default True. Can be set to False for self-signed certificates.
        """
        if incluster:
            try:
                config.load_incluster_config()
            except config.config_exception.ConfigException as e:
                logger.error('Are you sure tests are executed from within k8s cluster?')
                raise e
        else:
            try:
                config.load_kube_config(kube_config)
            except TypeError:
                logger.error('Neither KUBECONFIG nor ~/.kube/config available.')
        self.v1 = client.CoreV1Api()
        self.batchv1 = client.BatchV1Api()
        if not cert_validation:
            self.v1.api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'] = ssl.CERT_NONE

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

    def filter_pods_names(self, pods):
        """Filter pod names for list of pods.

        Returns list of strings.

        - ``pods``:
          List of pods objects
        """
        return [pod.metadata.name for pod in pods]

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
        except json.JSONDecodeError as e:
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
        except json.JSONDecodeError as e:
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
        except json.JSONDecodeError as e:
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
