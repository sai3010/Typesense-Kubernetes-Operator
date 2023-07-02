# Typesense-Kubernetes-Operator
An operator for Typesense written in Python. Provides a way to manage [Typesense](https://typesense.org/) in various deployment configurations.
It is currently being worked on to be made production ready.

Please report an issue for improvement suggestions/feedback. This operator is being written with the help of [KOPF](https://github.com/nolar/kopf) framework.

# Project Scope
The general idea is to make deployment of Tyepsense on kubernetes easy by automating the entire process involved in creation of Typesense cluster 
```
kubectl create -f operator-config.yaml
```

# Quickstart

1. Use [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) or any other tool to create your own kubernets cluster.
2.  ```
    cd deploy
    ```
    Deploy the Custom Resource Definition
    ```
    kubectl create -f crd.yaml
    ```
3. Deploy rbac
    ```
    kubectl create -f rbac.yaml
    ```
4. Deploy the latest operator 
    ```
    kubectl create -f operator.yaml
    ```
5. Check if operator is up and running 
    ```
    kubectl get pods 
    ```
6. Once the operator is up and running, define the operator configurations by referring to the section below
7. Wait for the cluster to be created
    ```
    # Get Typesense pod status
    kubectl get pods -n <namespace>
    ```

# Operator configuration
- Sample configuration can be found in `operator-config.yaml`
- All the configuration must be specified under `spec` or `config`
- Supported configurations under `spec`
    - `replicas` : Number of replicas of typesense. `default is 3`
    - `namespace`: Namespace to be used for deployment. `default namespace is typesense`
    - `image` : Typesense production ready docker image. List can be found [here](https://hub.docker.com/r/typesense/typesense). By `default latest tag` will be pulled
    - `resources` : Resources for cpu and memory.
        defaults to below configuration:
        ```
        resources:
          requests:
            memory: 100Mi
            cpu: "64m"
          limits:
            memory: 256Mi
            cpu: "512m"
        ```
    - `nodeSelector` : Node to which pod has to be scheduled
- Supported configurations under `config`
    - `password` : Typesense authentication is done using a password.` defaults to password`
    ## Deploying the configuration
    - `kubectl create -f operator-config.yaml`
    - To apply any changes made to the config
        - `kubectl apply -f operator-config.yaml`
    ## NOTE
    - Storace class is not yet supported, as of now typesense data will be temporarirly stored within the pod itself ,so taking a snaphot would be necessary
# Cleanup
- When you want to fully remove the cluster operator and associated definitions, you can run:
    ```
    kubectl delete -f operator-config.yaml
    kubectl delete -f deploy/crd.yaml
    kubectl delete -f deploy/operator.yaml
    kubectl delete -f deploy/rbac.yaml
    ```

# Getting help
If you encounter any issues while using the operator, you can get help by:
- Raise a Github issue

# Contributing
You can contribute by:
- Raising issues by opening Pull Requests
- Improving documentation

# License
Typesense operator is licensed under the [Apache License](./LICENSE)