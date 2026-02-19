"""
Performance Deep Metrics Module
Author: M. Nafiurohman
"""

import psutil
import os
from utils.helpers import run_cmd, IS_WINDOWS

def get_performance_metrics():
    """Get deep performance metrics"""
    try:
        metrics = {}
        
        # Context switches
        if hasattr(psutil, 'cpu_stats'):
            cpu_stats = psutil.cpu_stats()
            metrics['ctx_switches'] = cpu_stats.ctx_switches
            metrics['interrupts'] = cpu_stats.interrupts
            metrics['soft_interrupts'] = getattr(cpu_stats, 'soft_interrupts', 0)
        else:
            metrics['ctx_switches'] = 0
            metrics['interrupts'] = 0
            metrics['soft_interrupts'] = 0
        
        # File descriptors
        if not IS_WINDOWS:
            try:
                fd_count = len(os.listdir('/proc/self/fd'))
                fd_limit = int(run_cmd("ulimit -n") or "1024")
                metrics['file_descriptors'] = {
                    'current': fd_count,
                    'limit': fd_limit,
                    'percent': round((fd_count / fd_limit) * 100, 1)
                }
            except:
                metrics['file_descriptors'] = {'current': 0, 'limit': 0, 'percent': 0}
        else:
            metrics['file_descriptors'] = {'current': 0, 'limit': 0, 'percent': 0}
        
        # Process stats
        metrics['total_threads'] = sum([p.num_threads() for p in psutil.process_iter() if hasattr(p, 'num_threads')])
        metrics['total_processes'] = len(psutil.pids())
        
        # Zombie processes
        zombies = len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'zombie'])
        metrics['zombie_processes'] = zombies
        
        # Load average
        if hasattr(psutil, 'getloadavg'):
            load = psutil.getloadavg()
            metrics['load_average'] = {
                '1min': round(load[0], 2),
                '5min': round(load[1], 2),
                '15min': round(load[2], 2)
            }
        else:
            metrics['load_average'] = {'1min': 0, '5min': 0, '15min': 0}
        
        return metrics
    except Exception as e:
        return {'error': str(e)}

def get_resource_limits():
    """Get resource limits and exhaustion status"""
    try:
        limits = {}
        
        if not IS_WINDOWS:
            # Max open files
            try:
                max_files = run_cmd("cat /proc/sys/fs/file-max")
                current_files = run_cmd("cat /proc/sys/fs/file-nr | awk '{print $1}'")
                limits['open_files'] = {
                    'current': int(current_files or 0),
                    'max': int(max_files or 0),
                    'percent': round((int(current_files or 0) / int(max_files or 1)) * 100, 1)
                }
            except:
                limits['open_files'] = {'current': 0, 'max': 0, 'percent': 0}
            
            # Max user processes
            try:
                max_proc = run_cmd("ulimit -u")
                limits['max_processes'] = int(max_proc or 0)
            except:
                limits['max_processes'] = 0
            
            # Socket exhaustion
            try:
                sockets = len(psutil.net_connections())
                limits['sockets'] = sockets
            except:
                limits['sockets'] = 0
            
            # Ephemeral ports
            try:
                port_range = run_cmd("cat /proc/sys/net/ipv4/ip_local_port_range")
                if port_range:
                    parts = port_range.split()
                    if len(parts) == 2:
                        limits['ephemeral_ports'] = {
                            'min': int(parts[0]),
                            'max': int(parts[1]),
                            'range': int(parts[1]) - int(parts[0])
                        }
            except:
                pass
            
            # Inode usage
            try:
                df_output = run_cmd("df -i / | tail -1")
                if df_output:
                    parts = df_output.split()
                    if len(parts) >= 5:
                        limits['inodes'] = {
                            'used': parts[2],
                            'total': parts[1],
                            'percent': parts[4].replace('%', '')
                        }
            except:
                pass
        
        return limits
    except Exception as e:
        return {'error': str(e)}

def get_thermal_power():
    """Get thermal and power status"""
    try:
        thermal = {}
        
        # CPU Temperature
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                cpu_temps = []
                for name, entries in temps.items():
                    for entry in entries:
                        if 'cpu' in name.lower() or 'core' in entry.label.lower():
                            cpu_temps.append(entry.current)
                
                if cpu_temps:
                    thermal['cpu_temp'] = {
                        'current': round(max(cpu_temps), 1),
                        'average': round(sum(cpu_temps) / len(cpu_temps), 1),
                        'status': 'Normal' if max(cpu_temps) < 80 else 'Warning' if max(cpu_temps) < 90 else 'Critical'
                    }
        except:
            thermal['cpu_temp'] = {'current': 0, 'average': 0, 'status': 'N/A'}
        
        # Battery (if laptop)
        try:
            battery = psutil.sensors_battery()
            if battery:
                thermal['battery'] = {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else 'Unlimited'
                }
        except:
            thermal['battery'] = None
        
        # Thermal throttling (Linux)
        if not IS_WINDOWS:
            try:
                throttle = run_cmd("cat /sys/devices/system/cpu/cpu0/thermal_throttle/core_throttle_count")
                thermal['throttle_count'] = int(throttle or 0)
            except:
                thermal['throttle_count'] = 0
        
        return thermal
    except Exception as e:
        return {'error': str(e)}

def check_internet_connectivity():
    """Check internet connectivity"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return {'connected': True, 'latency': 'OK'}
    except:
        return {'connected': False, 'latency': 'N/A'}
