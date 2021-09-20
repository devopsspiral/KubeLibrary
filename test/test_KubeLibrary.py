import json
import mock
import re
import ssl
import unittest
from KubeLibrary import KubeLibrary, BearerTokenWithPrefixException
from kubernetes.config.config_exception import ConfigException
from urllib3_mock import Responses


class AttributeDict(object):
    """
    Based on http://databio.org/posts/python_AttributeDict.html

    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
    """
    def __init__(self, entries):
        self.add_entries(entries)

    def add_entries(self, entries):
        self._root = entries
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(value)
            elif type(value) is list:
                self.__dict__[key] = [AttributeDict(item) if type(item) is dict else item for item in value]
            else:
                self.__dict__[key] = value

    def __iter__(self):
        return iter(self._root)

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)


def mock_read_daemonset_details_in_namespace(name, namespace):
    if namespace == 'default':
        with open('test/resources/daemonset_details.json') as json_file:
            daemonset_details_content = json.load(json_file)
            read_daemonset_details = AttributeDict({'items': daemonset_details_content})
            return read_daemonset_details


def mock_read_service_details_in_namespace(name, namespace):
    if namespace == 'default':
        with open('test/resources/service_details.json') as json_file:
            service_details_content = json.load(json_file)
            read_service_details = AttributeDict({'items': service_details_content})
            return read_service_details


def mock_read_hpa_details_in_namespace(name, namespace):
    if namespace == 'default':
        with open('test/resources/hpa_details.json') as json_file:
            hpa_details_content = json.load(json_file)
            read_hpa_details = AttributeDict({'items': hpa_details_content})
            return read_hpa_details


def mock_read_ingress_details_in_namespace(name, namespace):
    if namespace == 'default':
        with open('test/resources/ingress_details.json') as json_file:
            ingress_details_content = json.load(json_file)
            read_ingress_details = AttributeDict({'items': ingress_details_content})
            return read_ingress_details


def mock_read_cron_job_details_in_namespace(name, namespace):
    if namespace == 'default':
        with open('test/resources/cronjob_details.json') as json_file:
            cron_job_details_content = json.load(json_file)
            read_cron_job_details = AttributeDict({'items': cron_job_details_content})
            return read_cron_job_details


def mock_list_namespaced_daemonsets(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/daemonset.json') as json_file:
            daemonsets_content = json.load(json_file)
            list_of_daemonsets = AttributeDict({'items': daemonsets_content})
            return list_of_daemonsets


def mock_list_namespaced_cronjobs(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/cronjob.json') as json_file:
            cronjobs_content = json.load(json_file)
            list_of_cronjobs = AttributeDict({'items': cronjobs_content})
            return list_of_cronjobs


def mock_list_namespaced_ingresses(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/ingress.json') as json_file:
            ingresses_content = json.load(json_file)
            list_ingresses = AttributeDict({'items': ingresses_content})
            return list_ingresses


def mock_read_namespaced_endpoints(name, namespace):
    if namespace == 'default':
        with open('test/resources/endpoints.json') as json_file:
            endpoints_content = json.load(json_file)
            read_endpoints = AttributeDict({'items': endpoints_content})
            return read_endpoints


def mock_list_namespaced_config_map(namespace, watch=False, label_selector=""):
    with open('test/resources/configmap.json') as json_file:
        configmap_content = json.load(json_file)
        configmap = AttributeDict({'items': configmap_content})
        return configmap


def mock_list_namespaced_deployments(namespace, watch=False, label_selector=""):
    with open('test/resources/deployment.json') as json_file:
        deployments_content = json.load(json_file)
        deployments = AttributeDict({'items': deployments_content})
        return deployments


def mock_list_namespaced_replicasets(namespace, watch=False, label_selector=""):
    with open('test/resources/replicaset.json') as json_file:
        replicasets_content = json.load(json_file)
        replicasets = AttributeDict({'items': replicasets_content})
        return replicasets


def mock_list_pvc(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/pvc.json') as json_file:
            pvc_content = json.load(json_file)
            list_pvc = AttributeDict({'items': pvc_content})
            return list_pvc


def mock_list_cluster_roles(watch=False):
    with open('test/resources/cluster_role.json') as json_file:
        cluster_roles_content = json.load(json_file)
        list_of_cluster_roles = AttributeDict({'items': cluster_roles_content})
        return list_of_cluster_roles


def mock_list_namespaced_services(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/service.json') as json_file:
            services_content = json.load(json_file)
            list_services = AttributeDict({'items': services_content})
            return list_services


def mock_list_namespaced_hpas(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/hpa.json') as json_file:
            hpas_content = json.load(json_file)
            list_hpas = AttributeDict({'items': hpas_content})
            return list_hpas


def mock_list_namespaced_pod(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/pods.json') as json_file:
            pods_content = json.load(json_file)
            list_of_pods = AttributeDict({'items': pods_content})
            return list_of_pods


def mock_list_cluster_role_bindings(watch=False):
    with open('test/resources/cluster_role_bind.json') as json_file:
        cluster_role_bindings_content = json.load(json_file)
        list_of_cluster_role_bindings = AttributeDict({'items': cluster_role_bindings_content})
        return list_of_cluster_role_bindings


def mock_list_namespaced_service_accounts(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/service_accounts.json') as json_file:
            service_accounts_content = json.load(json_file)
            list_of_service_accounts = AttributeDict({'items': service_accounts_content})
            return list_of_service_accounts


def mock_list_namespaced_jobs(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/jobs.json') as json_file:
            jobs_content = json.load(json_file)
            list_of_jobs = AttributeDict({'items': jobs_content})
            return list_of_jobs


def mock_list_namespaced_secrets(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/secrets.json') as json_file:
            secrets_content = json.load(json_file)
            list_of_secrets = AttributeDict({'items': secrets_content})
            return list_of_secrets


def mock_list_namespaces(watch=False, label_selector=""):
    with open('test/resources/namespaces.json') as json_file:
        namespaces_content = json.load(json_file)
        list_of_namespaces = AttributeDict({'items': namespaces_content})
        return list_of_namespaces


def mock_list_node_info(watch=False, label_selector=""):
    with open('test/resources/node_info.json') as json_file:
        node_info_content = json.load(json_file)
        node_info = AttributeDict(node_info_content)
        return node_info


def mock_list_namespaced_roles(namespace, watch=False):
    if namespace == 'default':
        with open('test/resources/role.json') as json_file:
            role_content = json.load(json_file)
            list_of_role = AttributeDict({'items': role_content})
            return list_of_role


def mock_list_namespaced_role_bindings(namespace, watch=False):
    if namespace == 'default':
        with open('test/resources/rolebinding.json') as json_file:
            role_bind_content = json.load(json_file)
            list_of_role_bind = AttributeDict({'items': role_bind_content})
            return list_of_role_bind


bearer_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjdXVWJMOUdTaDB1TjcyNmF0Sjk4RWlzQ05RaWdSUFoyN004TmlGT1pSX28ifQ.' \
               'eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1' \
               'lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im15c2EtdG' \
               '9rZW4taDRzNzUiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibXlzY' \
               'SIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjY5MTk5ZmUyLTIzNWIt' \
               'NGY3MC04MjEwLTkzZTk2YmM5ZmEwOCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om15c2EifQ.' \
               'V8VIYZ0B2y2h9p-2LTZ19klSuZ37HUWi-8F1yjfFTq83R1Dmax6DoDr5gWbVL4A054q5k1L2U12d50gox0V_kVsRTb3' \
               'KQnRSGCz1YgCqOVNLqnnsyu3kcmDaUDrFlJ4PuZ7R4DfvGCdK-BU9pj2MhcQT-tyfbGR-dwwkjwXTCPRZVW-CUm4qwY' \
               'bCGTpGbNXPXbEKtseXIxMkRg70Kav3M-YB1LYHQRx_T2IqKAmyhXlbMc8boqoEiSi6TRbMjZ9Yz-nkc82e6kAdc1O2F' \
               '4kFw-14kg2mX7Hu-02vob_LZmfR08UGu6VTkcfVK5VqZVg2oVBI4swZghQl8_fOtlplOg'

ca_cert = '/path/to/certificate.crt'

k8s_api_url = 'https://0.0.0.0:38041'

responses = Responses('requests.packages.urllib3')


class TestKubeLibrary(unittest.TestCase):

    apis = ('v1', 'extensionsv1beta1', 'batchv1', 'appsv1', 'batchv1_beta1',
            'custom_object', 'rbac_authv1_api', 'autoscalingv1', 'dynamic')

    @responses.activate
    def test_KubeLibrary_inits_from_kubeconfig(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        KubeLibrary(kube_config='test/resources/k3d')

    @responses.activate
    def test_KubeLibrary_inits_with_context(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        KubeLibrary(kube_config='test/resources/multiple_context', context='k3d-k3d-cluster2')

    @responses.activate
    def test_KubeLibrary_fails_for_wrong_context(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(kube_config='test/resources/multiple_context')
        self.assertRaises(ConfigException, kl.reload_config, kube_config='test/resources/multiple_context', context='k3d-k3d-cluster2-wrong')

    @responses.activate
    def test_inits_all_api_clients(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(kube_config='test/resources/k3d')
        for api in TestKubeLibrary.apis:
            self.assertIsNotNone(getattr(kl, api))

    @responses.activate
    def test_KubeLibrary_inits_without_cert_validation(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(kube_config='test/resources/k3d', cert_validation=False)
        for api in TestKubeLibrary.apis:
            target = getattr(kl, api)
            self.assertEqual(target.api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'], ssl.CERT_NONE)

    @responses.activate
    def test_KubeLibrary_inits_with_bearer_token(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(api_url=k8s_api_url, bearer_token=bearer_token)
        for api in TestKubeLibrary.apis:
            target = getattr(kl, api)
            self.assertEqual(kl.api_client.configuration.api_key, target.api_client.configuration.api_key)
        self.assertEqual(kl.api_client.configuration.ssl_ca_cert, None)

    @responses.activate
    def test_inits_with_bearer_token_raises_BearerTokenWithPrefixException(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(api_url=k8s_api_url, bearer_token=bearer_token)
        self.assertRaises(BearerTokenWithPrefixException, kl.reload_config, api_url=k8s_api_url, bearer_token='Bearer prefix should fail')

    @responses.activate
    def test_KubeLibrary_inits_with_bearer_token_with_ca_crt(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        kl = KubeLibrary(api_url=k8s_api_url, bearer_token=bearer_token, ca_cert=ca_cert)
        self.assertEqual(kl.api_client.configuration.ssl_ca_cert, ca_cert)
        self.assertEqual(kl.dynamic.configuration.ssl_ca_cert, ca_cert)
        self.assertEqual(kl.dynamic.client.configuration.ssl_ca_cert, ca_cert)

    @responses.activate
    def test_KubeLibrary_dynamic_init(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        kl = KubeLibrary(kube_config='test/resources/k3d')
        resource = kl.get_dynamic_resource("v1", "Pod")
        self.assertTrue(hasattr(resource, "get"))
        self.assertTrue(hasattr(resource, "watch"))
        self.assertTrue(hasattr(resource, "delete"))
        self.assertTrue(hasattr(resource, "create"))
        self.assertTrue(hasattr(resource, "patch"))
        self.assertTrue(hasattr(resource, "replace"))

    @responses.activate
    def test_KubeLibrary_dynamic_get(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        responses.add("GET", "/api/v1/mock/Mock", status=200,
                      body='{"api_version": "v1", "kind": "Pod", "name": "Mock", "msg": "My Mock Pod"}',
                      content_type="application/json")
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pod = kl.get("v1", "Pod", name="Mock")
        self.assertEqual(pod.msg, "My Mock Pod")

    @responses.activate
    def test_KubeLibrary_dynamic_patch(self):
        def mock_callback(request):
            self.assertEqual(request.body, '{"msg": "Mock"}')
            return (200, None, None)
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        responses.add_callback("PATCH", "/api/v1/mock/Mock", callback=mock_callback)
        kl = KubeLibrary(kube_config='test/resources/k3d')
        kl.patch("v1", "Pod", name="Mock", body={"msg": "Mock"})

    @responses.activate
    def test_KubeLibrary_dynamic_replace(self):
        def mock_callback(request):
            self.assertEqual(request.body, '{"msg": "Mock"}')
            return (200, None, None)
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        responses.add_callback("PUT", "/api/v1/mock/Mock", callback=mock_callback)
        kl = KubeLibrary(kube_config='test/resources/k3d')
        kl.replace("v1", "Pod", name="Mock", body={"msg": "Mock"})

    @responses.activate
    def test_KubeLibrary_dynamic_create(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        responses.add("POST", "/api/v1/mock", status=200)
        kl = KubeLibrary(kube_config='test/resources/k3d')
        kl.create("v1", "Pod", name="Mock")

    @responses.activate
    def test_KubeLibrary_dynamic_delete(self):
        responses.add("GET", "/version", status=200)
        responses.add("GET", "/apis", status=200, body='{"groups": [], "kind": "Pod" }', content_type="application/json")
        responses.add("GET", "/api/v1", status=200,
                      body='{"resources": [{"api_version": "v1", "kind": "Pod", "name": "Mock"}], "kind": "Pod"}',
                      content_type="application/json")
        responses.add("DELETE", "/api/v1/mock/Mock", status=200)
        kl = KubeLibrary(kube_config='test/resources/k3d')
        kl.delete("v1", "Pod", name="Mock")

    def test_generate_alphanumeric_str(self):
        name = KubeLibrary.generate_alphanumeric_str(10)
        self.assertEqual(10, len(name))

    def test_evaluate_callable_from_k8s_client(self):
        configmap = KubeLibrary.evaluate_callable_from_k8s_client(
            attr_name="V1ConfigMap",
            data={"msg": "Mock"}, api_version="v1", kind="ConfigMap",
            metadata=KubeLibrary.evaluate_callable_from_k8s_client(attr_name="V1ObjectMeta", name="Mock")
        )
        self.assertIsNotNone(configmap)
        self.assertEqual(configmap.metadata.name, "Mock")

    def test_filter_pods_names(self):
        pods_items = mock_list_namespaced_pod('default')
        kl = KubeLibrary(kube_config='test/resources/k3d')
        self.assertEqual(['octopus-0', 'grafana-5d9895c6c4-sfsn8'], kl.filter_pods_names(pods_items.items))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_get_all_pods_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('.*', 'default')
        self.assertEqual(['octopus-0', 'grafana-5d9895c6c4-sfsn8'], kl.filter_pods_names(pods))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_get_matching_pods_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('graf.*', 'default')
        self.assertEqual(['grafana-5d9895c6c4-sfsn8'], kl.filter_pods_names(pods))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_filter_pods_containers_by_name(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('octopus.*', 'default')
        self.assertEqual('manager', kl.filter_pods_containers_by_name(pods, '.*')[0].name)

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_filter_containers_images(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('octopus.*', 'default')
        containers = kl.filter_pods_containers_by_name(pods, '.*')
        self.assertEqual(['eu.gcr.io/kyma-project/incubator/develop/octopus:dc5dc284'], kl.filter_containers_images(containers))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_filter_pods_containers_statuses_by_name(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('octopus.*', 'default')
        self.assertEqual(0, kl.filter_pods_containers_statuses_by_name(pods, '.*')[0].restart_count)

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_pod')
    def test_filter_containers_resources(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_pod
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pods = kl.get_pods_in_namespace('octopus.*', 'default')
        containers = kl.filter_pods_containers_by_name(pods, '.*')
        self.assertEqual('100m', kl.filter_containers_resources(containers)[0].limits.cpu)

    def test_assert_pod_has_labels(self):
        pod = mock_list_namespaced_pod('default').items[0]
        kl = KubeLibrary(kube_config='test/resources/k3d')
        labels = '{}'
        self.assertTrue(kl.assert_pod_has_labels(pod, labels))
        labels = '{"app":"octopus"}'
        self.assertTrue(kl.assert_pod_has_labels(pod, labels))
        labels = '{"app":"wrong"}'
        self.assertFalse(kl.assert_pod_has_labels(pod, labels))
        labels = '{"notexists":"octopus"}'
        self.assertFalse(kl.assert_pod_has_labels(pod, labels))
        labels = '{"badlyformatted:}'
        self.assertTrue(kl.assert_pod_has_labels(pod, labels) is False)

    def test_assert_pod_has_annotations(self):
        pod = mock_list_namespaced_pod('default').items[1]
        kl = KubeLibrary(kube_config='test/resources/k3d')
        labels = '{}'
        self.assertTrue(kl.assert_pod_has_annotations(pod, labels))
        labels = '{"checksum/config":"1c42968a1b9eca0bafc3273ca39c4705fe71dc632e721db9e8ce44ab1b8e1428"}'
        self.assertTrue(kl.assert_pod_has_annotations(pod, labels))
        labels = '{"checksum/config":"wrong"}'
        self.assertFalse(kl.assert_pod_has_annotations(pod, labels))
        labels = '{"notexists":"1c42968a1b9eca0bafc3273ca39c4705fe71dc632e721db9e8ce44ab1b8e1428"}'
        self.assertFalse(kl.assert_pod_has_annotations(pod, labels))
        labels = '{"badlyformatted:}'
        self.assertTrue(kl.assert_pod_has_annotations(pod, labels) is False)

    def test_assert_container_has_env_vars(self):
        pod = mock_list_namespaced_pod('default').items[0]
        kl = KubeLibrary(kube_config='test/resources/k3d')
        container = kl.filter_pods_containers_by_name([pod], '.*')[0]
        env_vars = '{}'
        self.assertTrue(kl.assert_container_has_env_vars(container, env_vars))
        env_vars = '{"SECRET_NAME":"webhook-server-secret"}'
        self.assertTrue(kl.assert_container_has_env_vars(container, env_vars))
        env_vars = '{"SECRET_NAME":"wrong"}'
        self.assertFalse(kl.assert_container_has_env_vars(container, env_vars))
        env_vars = '{"NOT_EXISTING":"wrong"}'
        self.assertFalse(kl.assert_container_has_env_vars(container, env_vars))
        env_vars = '{"badlyformatted:}'
        self.assertFalse(kl.assert_container_has_env_vars(container, env_vars))

    @unittest.skip("Will overwrite test/resources/pods.json")
    def test_gather_pods_obejcts_to_pods_json(self):
        kl = KubeLibrary(kube_config='test/resources/k3d')
        ret = kl.v1.list_namespaced_pod('default', watch=False)
        pods_str = str(ret.items).replace("'", '"') \
                                 .replace('None', 'null') \
                                 .replace('True', 'true') \
                                 .replace('False', 'false')
        # serialize datetime into fixed timestamp
        pods = re.sub(r'datetime(.+?)\)\)', '1592598289', pods_str)
        with open('test/resources/pods.json', 'w') as outfile:
            json.dump(json.loads(pods), outfile, indent=4)

    @mock.patch('kubernetes.client.CoreV1Api.list_namespace')
    def test_list_namespaces(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaces
        kl = KubeLibrary(kube_config='test/resources/k3d')
        namespaces = kl.get_namespaces()
        self.assertTrue(len(namespaces) > 0)
        self.assertEqual(['default', 'kubelib-test-test-objects-chart'], namespaces)

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_service_account')
    def test_get_service_accounts_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_service_accounts
        kl = KubeLibrary(kube_config='test/resources/k3d')
        sa = kl.get_service_accounts_in_namespace('.*', 'default')
        self.assertEqual(['default', 'kubelib-test-test-objects-chart'], kl.filter_service_accounts_names(sa))

    @mock.patch('kubernetes.client.CoreV1Api.list_node')
    def test_get_kubelet_version(self, mock_lnp):
        mock_lnp.side_effect = mock_list_node_info
        kl = KubeLibrary(kube_config='test/resources/k3d')
        kl_version = kl.get_kubelet_version()
        self.assertTrue(len(kl_version) > 0)
        self.assertEqual(['v1.20.0+k3s2'], kl_version)

    @mock.patch('kubernetes.client.BatchV1Api.list_namespaced_job')
    def test_get_jobs_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_jobs
        kl = KubeLibrary(kube_config='test/resources/k3d')
        jobs = kl.get_jobs_in_namespace('.*', 'default')
        self.assertEqual(['octopus-0', 'octopus-1', 'octopus-2', 'octopus-3'], [item.metadata.name for item in jobs])

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_secret')
    def test_get_secrets_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_secrets
        kl = KubeLibrary(kube_config='test/resources/k3d')
        secrets = kl.get_secrets_in_namespace('.*', 'default')
        self.assertEqual(['grafana'], [item.metadata.name for item in secrets])

    @mock.patch('kubernetes.client.RbacAuthorizationV1Api.list_cluster_role')
    def test_get_cluster_roles_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_cluster_roles
        kl = KubeLibrary(kube_config='test/resources/k3d')
        cluster_roles = kl.get_cluster_roles()
        self.assertEqual(['secret-reader'], [item for item in cluster_roles])

    @mock.patch('kubernetes.client.RbacAuthorizationV1Api.list_cluster_role_binding')
    def test_get_cluster_role_bindings_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_cluster_role_bindings
        kl = KubeLibrary(kube_config='test/resources/k3d')
        cluster_role_bindings = kl.get_cluster_role_bindings()
        self.assertEqual(['read-secrets-global'], [item for item in cluster_role_bindings])

    @mock.patch('kubernetes.client.RbacAuthorizationV1Api.list_namespaced_role')
    def test_get_roles_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_roles
        kl = KubeLibrary(kube_config='test/resources/k3d')
        roles = kl.get_roles_in_namespace('default')
        self.assertEqual(['pod-reader'], [item for item in roles])

    @mock.patch('kubernetes.client.RbacAuthorizationV1Api.list_namespaced_role_binding')
    def test_get_role_bindings_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_role_bindings
        kl = KubeLibrary(kube_config='test/resources/k3d')
        role_bindings = kl.get_role_bindings_in_namespace('default')
        self.assertEqual(['read-pods'], [item for item in role_bindings])

    @mock.patch('kubernetes.client.AppsV1Api.list_namespaced_deployment')
    def test_get_deployments_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_deployments
        kl = KubeLibrary(kube_config='test/resources/k3d')
        deployments = kl.get_deployments_in_namespace('.*', 'default')
        self.assertEqual(['nginx-deployment'], kl.filter_deployments_names(deployments))

    @mock.patch('kubernetes.client.AppsV1Api.list_namespaced_replica_set')
    def test_get_replicasets_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_replicasets
        kl = KubeLibrary(kube_config='test/resources/k3d')
        replicasets = kl.get_replicasets_in_namespace('.*', 'test-auto')
        self.assertEqual(['nginx-proxy'], kl.filter_replicasets_names(replicasets))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_persistent_volume_claim')
    def test_get_pvc_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_pvc
        kl = KubeLibrary(kube_config='test/resources/k3d')
        pvcs = kl.get_pvc_in_namespace('default')
        self.assertEqual(['myclaim'], [item for item in pvcs])

    @mock.patch('kubernetes.client.AppsV1Api.list_namespaced_daemon_set')
    def test_get_daemonsets_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_daemonsets
        kl = KubeLibrary(kube_config='test/resources/k3d')
        daemonsets = kl.get_daemonsets_in_namespace('default')
        self.assertEqual(['fluentd-elasticsearch'], [item for item in daemonsets])

    @mock.patch('kubernetes.client.ExtensionsV1beta1Api.list_namespaced_ingress')
    def test_get_ingresses_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_ingresses
        kl = KubeLibrary(kube_config='test/resources/k3d')
        ingresses = kl.get_ingresses_in_namespace('default')
        self.assertEqual(['minimal-ingress'], [item for item in ingresses])

    @mock.patch('kubernetes.client.BatchV1beta1Api.list_namespaced_cron_job')
    def test_get_cronjobs_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_cronjobs
        kl = KubeLibrary(kube_config='test/resources/k3d')
        cronjobs = kl.get_cron_jobs_in_namespace('default')
        self.assertEqual(['hello'], [item for item in cronjobs])

    @mock.patch('kubernetes.client.CoreV1Api.read_namespaced_endpoints')
    def test_get_endpoints_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_namespaced_endpoints
        kl = KubeLibrary(kube_config='test/resources/k3d')
        endpoints = kl.get_endpoints_in_namespace('.*', 'default')
        self.assertEqual(['my-service'], kl.filter_endpoints_names(endpoints))

    @mock.patch('kubernetes.client.CoreV1Api.list_namespaced_config_map')
    def test_get_configmaps_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_config_map
        kl = KubeLibrary(kube_config='test/resources/k3d')
        configmaps = kl.get_configmaps_in_namespace('.*', 'default')
        self.assertEqual(['game-demo'], kl.filter_configmap_names(configmaps))

    @mock.patch('kubernetes.client.AutoscalingV1Api.list_namespaced_horizontal_pod_autoscaler')
    def test_get_hpas_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_list_namespaced_hpas
        kl = KubeLibrary(kube_config='test/resources/k3d')
        hpas = kl.get_hpas_in_namespace('default')
        self.assertEqual(['kubelib-test-test-objects-chart'], [item for item in hpas])

    @mock.patch('kubernetes.client.AutoscalingV1Api.read_namespaced_horizontal_pod_autoscaler')
    def test_get_hpa_details_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_hpa_details_in_namespace
        kl = KubeLibrary(kube_config='test/resources/k3d')
        hpa_details = kl.get_hpa_details_in_namespace('kubelib-test-test-objects-chart', 'default')
        self.assertEqual('kubelib-test-test-objects-chart', hpa_details.items.spec.scaleTargetRef.name)

    @mock.patch('kubernetes.client.AppsV1Api.read_namespaced_daemon_set')
    def test_get_daemonset_details_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_daemonset_details_in_namespace
        kl = KubeLibrary(kube_config='test/resources/k3d')
        daemonset_details = kl.get_daemonset_details_in_namespace('fluentd-elasticsearch', 'default')
        self.assertEqual('mytestlabel', daemonset_details.items.metadata.labels.TestLabel)

    @mock.patch('kubernetes.client.CoreV1Api.read_namespaced_service')
    def test_get_service_details_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_service_details_in_namespace
        kl = KubeLibrary(kube_config='test/resources/k3d')
        service_details = kl.get_service_details_in_namespace('minimal-ingress', 'default')
        self.assertEqual('mytest', service_details.items.metadata.labels.Test)

    @mock.patch('kubernetes.client.ExtensionsV1beta1Api.read_namespaced_ingress')
    def test_get_ingress_details_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_ingress_details_in_namespace
        kl = KubeLibrary(kube_config='test/resources/k3d')
        ingress_details = kl.get_ingress_details_in_namespace('max-ingress', 'default')
        self.assertEqual('mytestlabel', ingress_details.items.metadata.labels.TestLabel)

    @mock.patch('kubernetes.client.BatchV1beta1Api.read_namespaced_cron_job')
    def test_get_cron_job_details_in_namespace(self, mock_lnp):
        mock_lnp.side_effect = mock_read_cron_job_details_in_namespace
        kl = KubeLibrary(kube_config='test/resources/k3d')
        cron_job_details = kl.get_cron_job_details_in_namespace('hello', 'default')
        self.assertEqual('mytestlabel', cron_job_details.items.metadata.labels.TestLabel)
