import os
import psutil
from pathlib import Path

def get_directory_tree(path='/', max_depth=2, current_depth=0):
    """Get directory tree with file sizes"""
    try:
        if current_depth >= max_depth:
            return None
        
        path_obj = Path(path)
        if not path_obj.exists() or not path_obj.is_dir():
            return None
        
        result = {
            'name': path_obj.name or path,
            'path': str(path_obj),
            'type': 'directory',
            'children': []
        }
        
        try:
            items = sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items[:50]:  # Limit to 50 items
                if item.is_dir():
                    child = get_directory_tree(str(item), max_depth, current_depth + 1)
                    if child:
                        result['children'].append(child)
                else:
                    try:
                        size = item.stat().st_size
                        result['children'].append({
                            'name': item.name,
                            'path': str(item),
                            'type': 'file',
                            'size': size,
                            'size_human': format_bytes(size)
                        })
                    except:
                        pass
        except PermissionError:
            result['error'] = 'Permission denied'
        
        return result
    except:
        return None

def find_large_files(path='/', min_size_mb=100, max_results=50):
    """Find large files in directory"""
    large_files = []
    min_size = min_size_mb * 1024 * 1024
    
    try:
        for root, dirs, files in os.walk(path):
            # Skip system directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.cache']]
            
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    if size >= min_size:
                        large_files.append({
                            'path': filepath,
                            'name': file,
                            'size': size,
                            'size_human': format_bytes(size)
                        })
                except:
                    pass
            
            if len(large_files) >= max_results:
                break
        
        return sorted(large_files, key=lambda x: x['size'], reverse=True)[:max_results]
    except:
        return []

def get_storage_summary():
    """Get storage summary with filesystem details"""
    partitions = []
    
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent,
                'total_human': format_bytes(usage.total),
                'used_human': format_bytes(usage.used),
                'free_human': format_bytes(usage.free)
            })
        except:
            pass
    
    return partitions

def format_bytes(bytes_val):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"
