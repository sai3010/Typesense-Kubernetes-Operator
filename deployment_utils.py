import os,yaml,logging,datetime
from kubernetes.client.exceptions import ApiException

def validate_spec(op_spec: dict) -> dict:
    '''
    Function to validate the deployment yaml spec
    Param:
        op_spec : dict -> operator yaml file spec
    '''
    spec = op_spec['new'].get('spec',None)
    config = op_spec['new'].get('config',None)
    return_data = {}
    if spec:
        if spec.get('resources'):
            if spec.get('requests'):
                if not spec.get('memory') or spec.get('cpu'):
                    raise Exception("Memory or cpu is missing under requests")
            if spec.get('limits'):
                if not spec.get('memory') or spec.get('cpu'):
                    raise Exception("Memory or cpu is missing under limits")
        return_data['namespace'] = spec.get('namespace','typesense')
        return_data['image'] =  spec.get('image','typesense/typesense')
        return_data['resources'] = spec.get('resources',None)
        return_data['nodeSelector'] = spec.get('nodeSelector',None)
        return_data['replicas'] = spec.get('replicas',None)

    if config:
        return_data['password'] = config.get('password','297beb01dd21c')
    return return_data

def create_modify_namespace(core_obj: object,namespace='default') -> None:
    '''
    Function to create or modify namespace
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        path = os.path.join(
            os.path.dirname(__file__),
            'templates/namespace.yaml'
        )
        configuration = None
        with open(path,'r') as _file:
            configuration = yaml.safe_load(_file)
        if namespace !='default':
            configuration['metadata']['name'] = namespace
        try:
            resp = core_obj.create_namespace(body=configuration)
            logging.info(f"Created namespace {resp.metadata.name} successfully")
        except ApiException as e:
            logging.error(f"Kubernets Api Exception: {e.body} ")
    except Exception as e:
        logging.error(f"Exception namespace: {e}")
        

def deploy_typesense_statefulset(apps_obj: object,spec: dict,update=False) -> None:
    '''
    Function to deploy Typesense statefulset
    Params:
        apps_obj: kubernetes AppsV1Api object
    '''
    try:
        path = os.path.join(
            os.path.dirname(__file__),
            'templates/statefulset.yaml'
        )
        configuration = None
        with open(path,'r') as _file:
            configuration = yaml.safe_load(_file)
        # configuration['spec']['volumeClaimTemplates'][0]['spec']['storageClassName'] = spec['storageClassName']
        # configuration['spec']['volumeClaimTemplates'][0]['spec']['resources']['requests']['storage'] = spec['storage']
        configuration['metadata']['namespace'] = spec['namespace']
        if spec.get('resources'):
            configuration['spec']['template']['spec']['containers'][0]['resources'] = spec['resources']
        if spec.get('nodeSelector'):
            configuration['spec']['template']['spec']['nodeSelector'] = spec['nodeSelector']
        if spec.get('password'):
            configuration['spec']['template']['spec']['containers'][0]['command'][4] = spec['password']
        if spec.get('replicas'):
            configuration['spec']['replicas'] = spec['replicas']
        if update:
            configuration["spec"]["template"]["metadata"]["annotations"] = {
            "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow().isoformat()
            }
            apps_obj.patch_namespaced_stateful_set(
                body=configuration,name="typesense", namespace=spec['namespace'])
        else:
            apps_obj.create_namespaced_stateful_set(
                body=configuration, namespace=spec['namespace'])
    except ApiException as e:
        logging.error(f"Kubernets Api Exception: {e.body} ")
    except Exception as e:
        logging.error(f"Exception statefulset: {e}")
        

def deploy_configmap(core_obj: object,replicas=None,namespace='default',update=False) -> None:
    '''
    Function to create configmap used by Typesense
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        nodes = []
        path = os.path.join(
            os.path.dirname(__file__),
            'templates/configmap.yaml'
        )
        configuration = None
        with open(path,'r') as _file:
            configuration = yaml.safe_load(_file)
        if replicas:
            for count in range(0,int(replicas)):
                nodes.append(('typesense-{}.ts.typesense.svc.cluster.local:8107:8108').format(str(count)))
            configuration['data']['nodes'] = ','.join(nodes) 
        if update:
            core_obj.patch_namespaced_config_map(body=configuration,namespace=namespace,name="nodeslist")
        else:
            core_obj.create_namespaced_config_map(body=configuration,namespace=namespace)
        logging.info(f"Created Configmap nodeslist successfully")
    except ApiException as e:
        logging.error(f"Kubernets Api Exception: {e.body} ")
    except Exception as e:
        logging.error(f"Exception configmap: {e}")

def deploy_service(core_obj: object,namespace='default') -> None:
    '''
    Function to deploy service mapping to connect with Typesense
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        service_path = os.path.join(
            os.path.dirname(__file__),
            'templates/service.yaml'
        )
        configuration = None
        with open(service_path,'r') as _file:
            configuration = yaml.safe_load(_file)
        resp = core_obj.create_namespaced_service(body=configuration,namespace=namespace)

        logging.info(f"Created Service {resp.metadata.name} successfully")

        headless_service_path = os.path.join(
            os.path.dirname(__file__),
            'templates/headless-service.yaml'
        )
        with open(headless_service_path,'r') as _file:
            configuration = yaml.safe_load(_file)
        resp = core_obj.create_namespaced_service(body=configuration,namespace=namespace)

        logging.info(f"Created Headless Service {resp.metadata.name} successfully")
    except ApiException as e:
        logging.error(f"Kubernets Api Exception: {e.body} ")
    except Exception as e:
        logging.error(f"Exception service: {e}")

def cleanup(core_obj: object,namespace='default') -> None:
    '''
    Function to cleanup all resources
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        core_obj.delete_namespace(namespace)
    except ApiException as e:
        logging.error(f"Kubernets Api Exception: {e.body} ")
    except Exception as e:
        logging.error(f"Exception Cleanup: {e}")