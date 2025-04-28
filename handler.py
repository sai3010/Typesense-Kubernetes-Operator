import kopf
import logging
from kubernetes import client, config
from deployment_utils import validate_spec,deploy_typesense_statefulset,create_modify_namespace,deploy_configmap,deploy_service,cleanup
from routes import resource_create_count_success, resource_delete_count_success, resource_update_count_success

@kopf.on.login()
def login_fn(**kwargs):
    return kopf.login_with_service_account(**kwargs) or kopf.login_with_kubeconfig(**kwargs)

@kopf.on.create('TypesenseOperator',retries=3)
def create_fn(body, **kwargs):
    '''
    Create Typesense Operator
    `kubectl create -f operator.yaml`
    '''
    try:
        logging.info("----Loading incluster config----")
        config.load_incluster_config()
    except:
        logging.info("----Loading kube config----")
        config.load_kube_config()
    k8s_apps_v1 = client.AppsV1Api()
    k8s_core_v1 = client.CoreV1Api()
    operator_namespace = body.get('metadata', {}).get('namespace', 'default')
    kwargs['operator_namespace'] = operator_namespace
    spec = validate_spec(kwargs, k8s_core_v1)
    create_modify_namespace(k8s_core_v1,namespace=spec['namespace'])
    deploy_configmap(k8s_core_v1,replicas=spec['replicas'],namespace=spec['namespace'])
    deploy_service(k8s_core_v1,namespace=spec['namespace'])
    deploy_typesense_statefulset(k8s_apps_v1,spec)
    logging.info(f"Typesense Operator created successfully")
    resource_create_count_success.inc()

@kopf.on.update('TypesenseOperator', retries=3)
def update_fn(body, **kwargs):
    '''
    Patch update changes to operator
    `kubectl apply -f operator.yaml`
    '''
    try:
        logging.info("----Loading incluster config----")
        config.load_incluster_config()
    except:
        logging.info("----Loading kube config----")
        config.load_kube_config()
    k8s_apps_v1 = client.AppsV1Api()
    k8s_core_v1 = client.CoreV1Api()
    operator_namespace = body.get('metadata', {}).get('namespace', 'default')
    kwargs['operator_namespace'] = operator_namespace
    spec = validate_spec(kwargs, k8s_core_v1)
    deploy_configmap(k8s_core_v1,replicas=spec['replicas'],namespace=spec['namespace'],update=True)
    deploy_typesense_statefulset(k8s_apps_v1,spec,update=True)
    logging.info(f"Typesense Operator updated successfully")
    resource_update_count_success.inc()

@kopf.on.delete('TypesenseOperator', retries=3)
def delete_fn(body, **kwargs):
    '''
    Delete opeartor and its dependencies
    `kubectl delete -f operator.yaml`
    '''
    try:
        logging.info("----Loading incluster config----")
        config.load_incluster_config()
    except:
        logging.info("----Loading kube config----")
        config.load_kube_config()
    k8s_core_v1 = client.CoreV1Api()
    k8s_apps_v1 = client.AppsV1Api()
    spec = validate_spec(kwargs, k8s_core_v1, action='delete')
    cleanup(k8s_apps_v1,k8s_core_v1,spec['namespace'])
    logging.info(f"Typesense Operator cleaned successfully")
    resource_delete_count_success.inc()