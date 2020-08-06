# Helm chart to install requirements for the tests
With this helm chart kubernetes objects can be installed to a cluster as prerequisites to some of the tests for this library.

## Install with
Connect to your k8s cluster, then
```
kubectl create namespace kubelib-tests
helm install kubelib-test ./test-objects-chart -n kubelib-tests
```

## Extending this helm chart
Feel free to extend this helm chart which any other kubernetes objects which are required by any tests of this library.