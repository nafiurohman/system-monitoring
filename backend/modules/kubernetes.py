import subprocess
import json

def run_kubectl(command):
    """Run kubectl command"""
    try:
        result = subprocess.run(
            f"kubectl {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout if result.returncode == 0 else None
    except:
        return None

def get_k8s_pods():
    """Get Kubernetes pods"""
    output = run_kubectl("get pods -A -o json")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        pods = []
        
        for item in data.get('items', []):
            metadata = item.get('metadata', {})
            spec = item.get('spec', {})
            status = item.get('status', {})
            
            # Calculate restarts
            restarts = sum(cs.get('restartCount', 0) for cs in status.get('containerStatuses', []))
            
            pods.append({
                'name': metadata.get('name', 'N/A'),
                'namespace': metadata.get('namespace', 'default'),
                'status': status.get('phase', 'Unknown'),
                'restarts': restarts,
                'age': metadata.get('creationTimestamp', 'N/A'),
                'node': spec.get('nodeName', 'N/A'),
                'ip': status.get('podIP', 'N/A')
            })
        
        return pods
    except:
        return []

def get_k8s_services():
    """Get Kubernetes services"""
    output = run_kubectl("get services -A -o json")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        services = []
        
        for item in data.get('items', []):
            metadata = item.get('metadata', {})
            spec = item.get('spec', {})
            
            ports = ', '.join([f"{p.get('port')}/{p.get('protocol', 'TCP')}" 
                              for p in spec.get('ports', [])])
            
            services.append({
                'name': metadata.get('name', 'N/A'),
                'namespace': metadata.get('namespace', 'default'),
                'type': spec.get('type', 'ClusterIP'),
                'cluster_ip': spec.get('clusterIP', 'N/A'),
                'external_ip': spec.get('externalIPs', ['None'])[0] if spec.get('externalIPs') else 'None',
                'ports': ports or 'N/A'
            })
        
        return services
    except:
        return []

def get_k8s_deployments():
    """Get Kubernetes deployments"""
    output = run_kubectl("get deployments -A -o json")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        deployments = []
        
        for item in data.get('items', []):
            metadata = item.get('metadata', {})
            spec = item.get('spec', {})
            status = item.get('status', {})
            
            deployments.append({
                'name': metadata.get('name', 'N/A'),
                'namespace': metadata.get('namespace', 'default'),
                'replicas': spec.get('replicas', 0),
                'ready': status.get('readyReplicas', 0),
                'available': status.get('availableReplicas', 0),
                'age': metadata.get('creationTimestamp', 'N/A')
            })
        
        return deployments
    except:
        return []

def get_k8s_nodes():
    """Get Kubernetes nodes"""
    output = run_kubectl("get nodes -o json")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        nodes = []
        
        for item in data.get('items', []):
            metadata = item.get('metadata', {})
            status = item.get('status', {})
            
            # Get node status
            conditions = status.get('conditions', [])
            ready = next((c.get('status') for c in conditions if c.get('type') == 'Ready'), 'Unknown')
            
            nodes.append({
                'name': metadata.get('name', 'N/A'),
                'status': 'Ready' if ready == 'True' else 'NotReady',
                'roles': ', '.join(metadata.get('labels', {}).get('node-role.kubernetes.io', {}).keys()) or 'worker',
                'version': status.get('nodeInfo', {}).get('kubeletVersion', 'N/A'),
                'os': status.get('nodeInfo', {}).get('osImage', 'N/A')
            })
        
        return nodes
    except:
        return []

def is_k8s_available():
    """Check if kubectl is available"""
    return run_kubectl("version --client --short") is not None
