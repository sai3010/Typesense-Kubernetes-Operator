# Typesense-Kubernetes-Operator(WIP)
An operator for Typesense written in Python. Provides a way to manage [Typesense](https://typesense.org/) in various deployment configurations.
It is currently being worked on to be made production ready.

Please report an issue for improvement suggestions/feedback. This operator is being written with the help of [KOPF](https://github.com/nolar/kopf) framework.

# Project Scope
The general idea is to make deployment of Tyepsense on kubernetes easy by doing nothing more than `kubectl create -f operator-config.yaml`

# Quickstart

1. Use [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) or any other tool to create your own kubernets cluster.
2.  ```
    cd deploy
    ```
    Deploy the Custom Resource Definition
    ```
    kubectl apply -f crd.yaml
    ```
3. Deploy rbac
    ```
    kubectl apply -f rbac.yaml
    ```
4. Deploy the latest operator 
    ```
    kubectl apply -f operator.yaml
    ```
5. Check if operator is up and running 
    ```
    kubectl get pods 
    ```
6. Once the operator is up and running, define the operator configurations by referring to the document
7. Wait for the cluster to be created
    ```
    # Get Typesense pod status
    kubectl get pods -n <namespace>
    ```

# Cleanup
- When you want to fully remove the cluster operator and associated definitions, you can run:
    ```
    kubectl delete -f operator-config.yaml
    ```
# Deleting the operator
- When you want to fully remove the cluster operator and associated definitions, you can run:
    ```
    kubectl delete -f operator.yaml
    ```

# Getting help
If you encounter any issues while using the operator, you can get help by:
- Raise a Github issue

# Contributing
You can contribute by:
- Raising issues by opening Pull Requests
- Improving documentation