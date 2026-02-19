"""
GPU Monitoring Module - NVIDIA & AMD Support
Author: M. Nafiurohman
"""

import subprocess
from utils.helpers import run_cmd, IS_WINDOWS

def get_gpu_info():
    """Get GPU information for NVIDIA and AMD"""
    gpus = []
    
    # Try NVIDIA
    try:
        if IS_WINDOWS:
            nvidia_cmd = "nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free --format=csv,noheader,nounits"
        else:
            nvidia_cmd = "nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free --format=csv,noheader,nounits"
        
        result = run_cmd(nvidia_cmd)
        if result:
            for line in result.split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 7:
                        gpus.append({
                            'vendor': 'NVIDIA',
                            'name': parts[0],
                            'temperature': float(parts[1]) if parts[1] != '[N/A]' else 0,
                            'utilization': float(parts[2]) if parts[2] != '[N/A]' else 0,
                            'memory_utilization': float(parts[3]) if parts[3] != '[N/A]' else 0,
                            'memory_total': int(parts[4]) if parts[4] != '[N/A]' else 0,
                            'memory_used': int(parts[5]) if parts[5] != '[N/A]' else 0,
                            'memory_free': int(parts[6]) if parts[6] != '[N/A]' else 0
                        })
    except:
        pass
    
    # Try AMD (Linux only)
    if not IS_WINDOWS:
        try:
            amd_cmd = "rocm-smi --showtemp --showuse --showmeminfo vram"
            result = run_cmd(amd_cmd)
            if result and 'GPU' in result:
                gpus.append({
                    'vendor': 'AMD',
                    'name': 'AMD GPU',
                    'temperature': 0,
                    'utilization': 0,
                    'memory_utilization': 0,
                    'memory_total': 0,
                    'memory_used': 0,
                    'memory_free': 0
                })
        except:
            pass
    
    # Try Intel (basic detection)
    try:
        if IS_WINDOWS:
            intel_cmd = "wmic path win32_VideoController get name"
        else:
            intel_cmd = "lspci | grep -i vga"
        
        result = run_cmd(intel_cmd)
        if result and ('Intel' in result or 'intel' in result):
            if not any(gpu['vendor'] in ['NVIDIA', 'AMD'] for gpu in gpus):
                gpus.append({
                    'vendor': 'Intel',
                    'name': 'Intel Integrated Graphics',
                    'temperature': 0,
                    'utilization': 0,
                    'memory_utilization': 0,
                    'memory_total': 0,
                    'memory_used': 0,
                    'memory_free': 0
                })
    except:
        pass
    
    return {
        'available': len(gpus) > 0,
        'count': len(gpus),
        'gpus': gpus
    }
