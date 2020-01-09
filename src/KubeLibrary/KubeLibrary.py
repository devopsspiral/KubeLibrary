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

    = Kubecofnigs =

    Currently KubeLibrary is using only kubeconfig files. By default ~/.kube/config is used. Kubeconfig location
    can also be passed by setting KUBECONFIG environment variable or as Library argument.

    | ***** Settings *****
    | Library           KubeLibrary          True    /path/to/kubeconfig

    """
    def __init__(self, cert_validation=True, kube_config=None):
        """KubeLibrary can be configured with several optional arguments.
        - ``cert_validation``:
          Default True. Can be set to False for self-signed certificates.
        - ``kube_config``:
          Path pointing to kubeconfig of target Kubernetes cluster.
        """
        try:
            config.load_kube_config(kube_config)
        except TypeError:
            logger.error('Neither KUBECONFIG nor ~/.kube/config available.')
        self.v1 = client.CoreV1Api()
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

    def get_healthy_nodes_count(self):
        """Counts node with KubeletReady and status True.

        Can be used to check number of healthy nodes. Can be used as prerequisite in tests.
        """
        ret = self.v1.list_node(watch=False)
        healthy_nods = []
        for item in ret.items:
            for condition in item.status.conditions:
                if condition.reason == 'KubeletReady' and condition.status == 'True':
                    healthy_nods.append(item.metadata.name)
        return len(healthy_nods)


    def get_pods_in_namespace(self, namespace):
        """Gets pod names in given namespace.

        Returns list pf strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_pod(namespace, watch=False)
        return [item.metadata.name for item in ret.items]

    def get_pod_status_in_namespace(self, name, namespace):
        """Gets pod status in given namespace.

        - ``name``:
          Name of pod.
        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.read_namespaced_pod_status(name, namespace)
        return ret.status.phase


    def get_pods_images_in_namespace(self, pattern, namespace, exclude='|'):
        """Gets pods container images in given namespace.

        Returns list of strings.

        - ``pattern``:
          Name or part of the name of pod to include
        - ``namespace``:
          Namespace to check
        - ``exclude``:
          Part of pod name to exclude
        """
        ret = self.v1.list_namespaced_pod(namespace, watch=False)
        containers = [item.spec.containers for item in ret.items if pattern in item.metadata.name and exclude not in item.metadata.name]
        return [item.image for sublist in containers for item in sublist]

    def get_services_in_namespace(self, namespace):
        """Gets services in given namespace.

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_service(namespace, watch=False)
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

    def get_pvc_in_namespace(self, namespace):
        """Gets pvcs in given namespace.

        Returns list of strings.

        - ``namespace``:
          Namespace to check
        """
        ret = self.v1.list_namespaced_persistent_volume_claim(namespace, watch=False)
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

    def get_kubelet_version(self):
        """Gets list of kubelet versions on each node.

        Returns list of strings.
        """
        ret = self.v1.list_node(watch=False)
        return [item.status.node_info.kubelet_version for item in ret.items]


