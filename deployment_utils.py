import os,yaml,logging,datetime,json,base64
from kubernetes.client.exceptions import ApiException

def validate_spec(op_spec: dict, k8s_core_v1=None) -> dict:
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
        return_data['replicas'] = spec.get('replicas',3)
        if spec.get('storageClass'):
            if not spec['storageClass'].get('name') or not spec['storageClass'].get('size'):
                raise Exception('Missing storageClass name or size')
            return_data['storageClassName'] = spec['storageClass']['name']
            return_data['storage'] = spec['storageClass']['size']

        if spec.get('startupProbe'):
            if not spec['startupProbe'].get('failureThreshold') or not spec['startupProbe'].get('periodSeconds'):
                raise Exception('Missing startupProbe properties. Required: failureThreshold, periodSeconds')            
            return_data['startupProbe_failureThreshold'] = spec['startupProbe']['failureThreshold']
            return_data['startupProbe_periodSeconds'] = spec['startupProbe']['periodSeconds']

        if spec.get('livenessProbe'):
            if not spec['livenessProbe'].get('failureThreshold') or not spec['livenessProbe'].get('periodSeconds'):
                raise Exception('Missing livenessProbe properties. Required: failureThreshold, periodSeconds')            
            return_data['livenessProbe_failureThreshold'] = spec['livenessProbe']['failureThreshold']
            return_data['livenessProbe_periodSeconds'] = spec['livenessProbe']['periodSeconds']

    if config:
        '''
        Get APIKEY from secret
        '''
        secret_name = config.get('secret','typesense-apikey')
        secret = k8s_core_v1.read_namespaced_secret(name=secret_name,namespace=return_data['namespace'])
        secret_data = secret.data
        if not secret_data:
            raise Exception("Secret for APIKey not found")
        # Decode the base64 encoded secret data
        for key, value in secret_data.items():
            return_data['password'] = base64.b64decode(value).decode('utf-8')
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
            e.body = json.loads(e.body)
            if e.body['reason'] == "AlreadyExists":
                logging.info(f"Namespace exists, Skipping namespace creation!")
            else:
                logging.error(f"Kubernets Api Exception - Namespace: {e.body} ")
                raise Exception(f"Kubernets Api Exception - Namespace: {e.body}")
    except Exception as e:
        logging.error(f"Exception namespace: {e}")
        raise Exception(f"Exception namespace: {e}")
        

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
        if spec.get('storageClassName'):
            template = {
              "volumeClaimTemplates": [
                {
                  "metadata": {
                    "name": "data"
                  },
                  "spec": {
                    "accessModes": [
                      "ReadWriteOnce"
                    ],
                    "storageClassName": spec['storageClassName'],
                    "resources": {
                      "requests": {
                        "storage": spec['storage']
                      }
                    }
                  }
                }
              ]
            }
            configuration['spec']['volumeClaimTemplates'] = template['volumeClaimTemplates']
        else:
            # Use empty dir mount
            configuration['spec']['template']['spec']['volumes'].append({"name":"data","emptyDir":{"sizeLimit":"500Mi"}})
        configuration['metadata']['namespace'] = spec['namespace']
        
        # Determine the current index for the Typesense container.
        typesense_container_index = 0
        for index, container in enumerate(configuration['spec']['template']['spec']['containers']):
            if container['name'] == 'typesense':
                typesense_container_index = index
        
        logging.info(f"Using the index {typesense_container_index} to access the typesense container.")

        if spec.get('image'):
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['image'] = spec['image']
        if spec.get('resources'):
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['resources'] = spec['resources']
        if spec.get('nodeSelector'):
            configuration['spec']['template']['spec']['nodeSelector'] = spec['nodeSelector']
        if spec.get('password'):
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['command'][4] = spec['password']
        if spec.get('replicas'):
            configuration['spec']['replicas'] = spec['replicas']

        if spec.get('startupProbe_failureThreshold') and spec.get('startupProbe_periodSeconds'):            
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['startupProbe']['failureThreshold'] = spec['startupProbe_failureThreshold']
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['startupProbe']['periodSeconds'] = spec['startupProbe_periodSeconds']

        if spec.get('livenessProbe_failureThreshold') and spec.get('livenessProbe_periodSeconds'):            
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['livenessProbe']['failureThreshold'] = spec['livenessProbe_failureThreshold']
            configuration['spec']['template']['spec']['containers'][typesense_container_index]['livenessProbe']['periodSeconds'] = spec['livenessProbe_periodSeconds']
        
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
        logging.error(f"Kubernets Api Exception - Statefulset: {e.body} ")
        raise Exception(f"Kubernets Api Exception - Statefulset: {e.body} ")
    except Exception as e:
        logging.error(f"Exception statefulset: {e}")
        raise Exception(f"Exception statefulset: {e}")
        

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
        configuration['metadata']['namespace'] = namespace
        if replicas:
            for count in range(0,int(replicas)):
                nodes.append(('typesense-{}.ts.{}.svc.cluster.local:8107:8108').format(str(count),namespace))
            configuration['data']['nodes'] = ','.join(nodes) 
        if update:
            core_obj.patch_namespaced_config_map(body=configuration,namespace=namespace,name="nodeslist")
        else:
            core_obj.create_namespaced_config_map(body=configuration,namespace=namespace)
        logging.info(f"Created Configmap nodeslist successfully")
    except ApiException as e:
        logging.error(f"Kubernets Api Exception - Configmap: {e.body} ")
        raise Exception(f"Kubernets Api Exception - Configmap: {e.body} ")
    except Exception as e:
        logging.error(f"Exception configmap: {e}")
        raise Exception(f"Exception configmap: {e}")

def deploy_service(core_obj: object,namespace='default') -> None:
    '''
    Function to deploy service mapping to connect with Typesense
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        '''
        ----Deploy service---
        '''
        service_path = os.path.join(
            os.path.dirname(__file__),
            'templates/service.yaml'
        )
        configuration = None
        with open(service_path,'r') as _file:
            configuration = yaml.safe_load(_file)
        configuration['metadata']['namespace'] = namespace
        resp = core_obj.create_namespaced_service(body=configuration,namespace=namespace)

        logging.info(f"Created Service {resp.metadata.name} successfully")

        '''
        ----Deploy headless service---
        '''
        headless_service_path = os.path.join(
            os.path.dirname(__file__),
            'templates/headless-service.yaml'
        )
        with open(headless_service_path,'r') as _file:
            configuration = yaml.safe_load(_file)
        configuration['metadata']['namespace'] = namespace
        resp = core_obj.create_namespaced_service(body=configuration,namespace=namespace)

        logging.info(f"Created Headless Service {resp.metadata.name} successfully")
    except ApiException as e:
        logging.error(f"Kubernets Api Exception - Service: {e.body} ")
        raise Exception(f"Kubernets Api Exception - Service: {e.body} ")
    except Exception as e:
        logging.error(f"Exception service: {e}")
        raise Exception(f"Exception service: {e}")

def cleanup(apps_obj: object,core_obj: object,namespace='default') -> None:
    '''
    Function to cleanup all resources
    Params:
        core_obj: kubernetes CoreV1Api object
    '''
    try:
        # Delete configmap
        core_obj.delete_namespaced_config_map('nodeslist',namespace)
        # Delete headless service
        core_obj.delete_namespaced_service('ts',namespace)
        # Delete service
        core_obj.delete_namespaced_service('typesense-svc',namespace)
        # Delete statefulset
        apps_obj.delete_namespaced_stateful_set('typesense',namespace)
    except ApiException as e:
        e.body = json.loads(e.body)
        if e.body['reason'] == "NotFound":
            logging.info(f"Skipping Cleanup as {e.body['message']}")
        else:
            logging.error(f"Kubernets Api Exception - Cleanup: {e.body} ")
            raise Exception(f"Kubernets Api Exception - Cleanup: {e.body} ")
    except Exception as e:
        logging.error(f"Exception Cleanup: {e}")
        raise Exception(f"Exception Cleanup: {e}")