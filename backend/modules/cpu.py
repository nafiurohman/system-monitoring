"""
CPU Monitoring Module - High Performance
Author: M. Nafiurohman
"""

import psutil
import platform
from utils.helpers import get_cpu_name, IS_WINDOWS, run_cmd

def get_cpu_info():
    """Get detailed CPU information with per-thread monitoring"""
    try:
        cpu_freq = psutil.cpu_freq()
        cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
        
        # CPU temperature
        cpu_temp = 0
        try:
            if not IS_WINDOWS:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
                elif 'cpu_thermal' in temps:
                    cpu_temp = temps['cpu_thermal'][0].current
        except:
            pass
        
        # Cache size
        cache_size = "N/A"
        try:
            if IS_WINDOWS:
                cache = run_cmd("wmic cpu get L3CacheSize")
                if cache:
                    lines = cache.split('\n')
                    for line in lines:
                        if line.strip() and 'L3CacheSize' not in line:
                            cache_size = f"{line.strip()} KB"
                            break
            else:
                cache = run_cmd("lscpu | grep 'L3 cache' | awk '{print $3}'")
                cache_size = cache if cache else "N/A"
        except:
            pass
        
        # Get logical cores (threads)
        physical_cores = psutil.cpu_count(logical=False) or 0
        logical_cores = psutil.cpu_count(logical=True) or 0
        
        # Per-thread usage
        threads_usage = []
        for i, usage in enumerate(cpu_percent_per_core):
            threads_usage.append({
                'thread': i,
                'usage': round(usage, 1)
            })
        
        return {
            'model': get_cpu_name(),
            'cores': physical_cores,
            'threads': logical_cores,
            'frequency': {
                'current': round(cpu_freq.current, 2) if cpu_freq else 0,
                'min': round(cpu_freq.min, 2) if cpu_freq else 0,
                'max': round(cpu_freq.max, 2) if cpu_freq else 0
            },
            'usage_per_core': cpu_percent_per_core,
            'threads_usage': threads_usage,
            'usage_total': round(sum(cpu_percent_per_core) / len(cpu_percent_per_core), 1),
            'load_average': {
                '1min': round(load_avg[0], 2),
                '5min': round(load_avg[1], 2),
                '15min': round(load_avg[2], 2)
            },
            'temperature': round(cpu_temp, 1),
            'cache_size': cache_size
        }
    except Exception as e:
        return {'error': str(e)}
