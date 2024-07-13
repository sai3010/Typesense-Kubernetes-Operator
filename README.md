# Typesense-Kubernetes-Operator
An operator for Typesense written in Python. Provides a way to manage [Typesense](https://typesense.org/) in various deployment configurations.
It is currently being worked on to be made production ready.

Please report an issue for improvement suggestions/feedback. This operator is being written with the help of [KOPF](https://github.com/nolar/kopf) framework.

# Project Scope
The general idea is to make deployment of Typesense on kubernetes easy by automating the entire process involved in creation of Typesense cluster
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
    - `replicas` : Number of replicas of typesense. default is `3` <br>
        **NOTE**: When the number of replicas are increased the operator automatically handles the peering connection between the replicas.
    - `namespace`: Namespace to be used for deployment. default namespace is `typesense`
    - `image` : Typesense production ready docker image. List can be found [here](https://hub.docker.com/r/typesense/typesense). By default `latest` tag will be pulled
    - `resources` : Resources for cpu and memory.<br>
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
    - `nodeSelector` : Node to which pod has to be scheduled. if not specified, it picks up the node with available resources
    - `storageClass` : Provides a way to administor the storage. Create a storage class with the provider of your choice and add it to the operator config.<br>
    Options available are `name` and `size`
        - `name` : Name of the storageClass that the operator should consider for volume mount.
        - `size` : Size of the volume to be allocated to each typesense replica.<br>
        **NOTE**: Supports all [k8s Storageclass](https://kubernetes.io/docs/concepts/storage/storage-classes/).
    - `startupProbe` : Protect slow starting containers with startup probes <br>
    Options available are `failureThreshold` and `periodSeconds` <br>
    **NOTE**: [k8s startupProbe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-startup-probes).
    - `livenessProbe` :  Kubernetes provides liveness probes to detect and remedy such situations. <br>
    Options available are `failureThreshold` and `periodSeconds`<br>
    **NOTE**: [k8s livenessProbe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-a-liveness-http-request).
- Supported configurations under `config`
    - `password` : Typesense authentication is done using a password. defaults to `297beb01dd21c`
    ## Deploying the configuration
    - `kubectl create -f operator-config.yaml`
    - To apply any changes made to the config
        - `kubectl apply -f operator-config.yaml`

# Upgrade
- Before performing this upgrade process, it is recommended to:
    - Test it out in a dev environment 
    - Backup the Typesense data
- The process of updating TKO is simple:
    1. Watch for changes in the CRD file and apply those changes
    2. Watch for changes in the RBAC file and apply those changes
    3. Apply the new `operator.yaml` file
    4. Once the new operator pod is up and running, re-apply the configuration of the your operator so that the changes (if any) are reflected.<br>
        ```kubectl apply -f <your operator config file yaml>```

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
- Raising an issue
- Opening Pull Requests
- Improving documentation

# License
Typesense operator is licensed under the [Apache License](./LICENSE)