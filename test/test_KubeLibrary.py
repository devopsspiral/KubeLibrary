
import json
import mock
import re
import unittest
from KubeLibrary import KubeLibrary
from kubernetes.config.config_exception import ConfigException


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


def mock_list_namespaced_pod(namespace, watch=False, label_selector=""):
    if namespace == 'default':
        with open('test/resources/pods.json') as json_file:
            pods_content = json.load(json_file)
            list_of_pods = AttributeDict({'items': pods_content})
            return list_of_pods


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


class TestKubeLibrary(unittest.TestCase):

    def test_KubeLibrary_inits_from_kubeconfig(self):
        KubeLibrary(kube_config='test/resources/k3d')

    def test_KubeLibrary_inits_with_context(self):
        KubeLibrary(kube_config='test/resources/multiple_context', context='k3d-k3d-cluster2')

    def test_KubeLibrary_fails_for_wrong_context(self):
        kl = KubeLibrary(kube_config='test/resources/multiple_context')
        self.assertRaises(ConfigException, kl.reload_config, kube_config='test/resources/multiple_context', context='k3d-k3d-cluster2-wrong')

    def test_KubeLibrary_inits_without_cert_validation(self):
        KubeLibrary(kube_config='test/resources/k3d', cert_validation=False)

    def test_KubeLibrary_inits_with_bearer_token(self):
        KubeLibrary(auth={'bearer_token': (k8s_api_url, bearer_token, ca_cert)})

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
