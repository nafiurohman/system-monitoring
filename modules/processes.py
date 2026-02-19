"""
Process Manager Module - Task Manager Style
Author: M. Nafiurohman
"""

import psutil
from datetime import datetime

def get_process_list():
    """Get detailed process list like Task Manager"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time', 'num_threads']):
        try:
            # Get IO counters if available
            try:
                io_counters = proc.io_counters()
            except:
                io_counters = None
            
            # Get network connections count
            try:
                connections = len(proc.connections())
            except:
                connections = 0
            
            process_info = {
                'pid': proc.info.get('pid', 0),
                'name': proc.info.get('name', 'Unknown'),
                'user': proc.info.get('username') or 'N/A',
                'cpu': round(proc.info.get('cpu_percent') or 0, 1),
                'memory': round(proc.info.get('memory_percent') or 0, 1),
                'memory_mb': round((proc.info.get('memory_info').rss / 1024 / 1024) if proc.info.get('memory_info') else 0, 1),
                'status': proc.info.get('status', 'unknown'),
                'threads': proc.info.get('num_threads') or 0,
                'connections': connections,
                'disk_read': 0,
                'disk_write': 0,
                'started': datetime.fromtimestamp(proc.info.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S') if proc.info.get('create_time') else 'N/A'
            }
            
            # Add IO if available
            if io_counters:
                process_info['disk_read'] = io_counters.read_bytes
                process_info['disk_write'] = io_counters.write_bytes
            
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue
    
    return {
        'total': len(processes),
        'processes': processes
    }

def get_process_summary():
    """Get process summary statistics"""
    try:
        total = len(psutil.pids())
        running = len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running'])
        sleeping = len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping'])
        
        return {
            'total': total,
            'running': running,
            'sleeping': sleeping,
            'threads': sum([p.num_threads() for p in psutil.process_iter() if hasattr(p, 'num_threads')])
        }
    except:
        return {'total': 0, 'running': 0, 'sleeping': 0, 'threads': 0}
