#!/usr/bin/env python3
"""
System Monitor Dashboard
Professional server monitoring platform

Author: M. Nafiurohman
Website: https://nafiurohman.pages.dev
GitHub: https://github.com/nafiurohman
Email: nafiurohman25@gmail.com

Copyright (c) 2026 M. Nafiurohman
MIT License

DO NOT REMOVE THIS COPYRIGHT NOTICE
"""

from flask import Flask, render_template, jsonify, request
import psutil
import platform
import socket
import subprocess
import os
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
import re
import logging

# Import modular components for better performance
from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.gpu import get_gpu_info
from modules.security import get_security_info as get_security_info_enhanced
from modules.processes import get_process_list, get_process_summary
from modules.storage import get_directory_tree, find_large_files, get_storage_summary
from modules.network_enhanced import get_network_traffic_details, get_network_connections_detailed
from modules.kubernetes import get_k8s_pods, get_k8s_services, get_k8s_deployments, get_k8s_nodes, is_k8s_available
from modules.performance import get_performance_metrics, get_resource_limits, get_thermal_power, check_internet_connectivity
from utils.helpers import run_cmd, IS_WINDOWS

# Version
VERSION = "mntr26.02.19-14.38"

# Disable Flask default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Cache untuk optimasi
cache = {}
cache_time = {}
CACHE_TTL = 0.5  # 0.5 second for ultra real-time data

def get_cached(key, func):
    """Cache dengan TTL"""
    now = time.time()
    if key in cache and (now - cache_time.get(key, 0)) < CACHE_TTL:
        return cache[key]
    data = func()
    cache[key] = data
    cache_time[key] = now
    return data

def run_cmd(cmd):
    """Jalankan command shell - DEPRECATED, use utils.helpers.run_cmd"""
    from utils.helpers import run_cmd as helper_run_cmd
    return helper_run_cmd(cmd)

# ==================== SYSTEM INFO ====================
def get_system_info():
    """Identitas server lengkap"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Deteksi virtualisasi
        virt_type = run_cmd("systemd-detect-virt") or "baremetal"
        
        # NTP status
        ntp_status = "active" if "active" in run_cmd("timedatectl status | grep 'NTP service'") else "inactive"
        
        return {
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'os': f"{platform.system()} {platform.release()}",
            'os_version': platform.version(),
            'kernel': platform.release(),
            'architecture': platform.machine(),
            'virtualization': virt_type,
            'hypervisor': run_cmd("lscpu | grep Hypervisor | awk '{print $3}'") if virt_type != "none" else "N/A",
            'timezone': run_cmd("timedatectl | grep 'Time zone' | awk '{print $3}'"),
            'system_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ntp_status': ntp_status,
            'uptime': str(uptime).split('.')[0],
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== HARDWARE ====================
# CPU and Memory now use modular imports
# See modules/cpu.py and modules/memory.py

def get_disk_info():
    """Informasi disk lengkap"""
    try:
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                io = psutil.disk_io_counters(perdisk=False)
                
                # SMART status
                smart_status = run_cmd(f"smartctl -H {part.device} 2>/dev/null | grep 'SMART overall-health'")
                
                partitions.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'read_bytes': io.read_bytes if io else 0,
                    'write_bytes': io.write_bytes if io else 0,
                    'read_count': io.read_count if io else 0,
                    'write_count': io.write_count if io else 0,
                    'smart_status': 'PASSED' if 'PASSED' in smart_status else 'UNKNOWN'
                })
            except:
                continue
        
        return {'partitions': partitions}
    except Exception as e:
        return {'error': str(e)}

# ==================== NETWORK ====================
def get_network_info():
    """Informasi network lengkap"""
    try:
        interfaces = []
        stats = psutil.net_io_counters(pernic=True)
        addrs = psutil.net_if_addrs()
        
        # Public IP
        public_ip = run_cmd("curl -s ifconfig.me") or "N/A"
        
        for iface, addr_list in addrs.items():
            stat = stats.get(iface)
            
            ip_addr = ""
            mac_addr = ""
            
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    ip_addr = addr.address
                elif addr.family == psutil.AF_LINK:
                    mac_addr = addr.address
            
            # Link speed
            link_speed = run_cmd(f"ethtool {iface} 2>/dev/null | grep Speed | awk '{{print $2}}'") or "N/A"
            
            # Status
            status = "UP" if psutil.net_if_stats()[iface].isup else "DOWN"
            
            interfaces.append({
                'name': iface,
                'ip': ip_addr,
                'mac': mac_addr,
                'status': status,
                'link_speed': link_speed,
                'bytes_sent': stat.bytes_sent if stat else 0,
                'bytes_recv': stat.bytes_recv if stat else 0,
                'packets_sent': stat.packets_sent if stat else 0,
                'packets_recv': stat.packets_recv if stat else 0,
                'errin': stat.errin if stat else 0,
                'errout': stat.errout if stat else 0,
                'dropin': stat.dropin if stat else 0,
                'dropout': stat.dropout if stat else 0
            })
        
        # TCP connections
        connections = psutil.net_connections(kind='inet')
        established = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        # Firewall status
        ufw_status = run_cmd("ufw status | head -1")
        
        # Open ports
        open_ports = run_cmd("ss -tuln | grep LISTEN | awk '{print $5}' | cut -d':' -f2 | sort -u")
        
        return {
            'interfaces': interfaces,
            'public_ip': public_ip,
            'connections': {
                'total': len(connections),
                'established': established
            },
            'firewall': {
                'ufw_status': ufw_status,
                'open_ports': open_ports.split('\n') if open_ports else []
            }
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== PROCESSES ====================
def get_processes_info():
    """Informasi proses"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except:
                continue
        
        # Sort by CPU
        top_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
        
        # Sort by Memory
        top_mem = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:10]
        
        # Zombie processes
        zombies = [p for p in processes if p.get('status') == 'zombie']
        
        return {
            'total': len(processes),
            'top_cpu': top_cpu,
            'top_memory': top_mem,
            'zombies': zombies
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== SERVICES ====================
def get_services_info():
    """Informasi services - Windows & Linux compatible"""
    try:
        service_list = []
        
        if IS_WINDOWS:
            # Windows services
            services = ['W3SVC', 'MSSQLSERVER', 'MySQL', 'postgresql-x64-14', 'Redis', 'Docker', 'sshd']
            for svc in services:
                try:
                    status = run_cmd(f'sc query "{svc}" | findstr STATE')
                    if status:
                        is_running = 'RUNNING' in status
                        service_list.append({
                            'name': svc,
                            'status': 'active' if is_running else 'inactive',
                            'enabled': 'enabled',
                            'pid': 'N/A'
                        })
                except:
                    pass
        else:
            # Linux services
            services = ['nginx', 'apache2', 'mysql', 'mariadb', 'postgresql', 'redis', 'php-fpm', 'ssh', 'docker', 'cron']
            for svc in services:
                status = run_cmd(f"systemctl is-active {svc} 2>/dev/null")
                enabled = run_cmd(f"systemctl is-enabled {svc} 2>/dev/null")
                
                if status or enabled:
                    # Get PID
                    pid = run_cmd(f"systemctl show {svc} --property=MainPID --value")
                    
                    service_list.append({
                        'name': svc,
                        'status': status,
                        'enabled': enabled,
                        'pid': pid
                    })
        
        return {
            'services': service_list,
            'total': len(service_list),
            'running': len([s for s in service_list if s['status'] == 'active'])
        }
    except Exception as e:
        return {'error': str(e), 'services': [], 'total': 0, 'running': 0}

# ==================== SECURITY ====================
def get_security_info():
    """Informasi security"""
    try:
        # Failed login attempts
        failed_logins = run_cmd("grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -20")
        
        # Currently logged users
        users = []
        for user in psutil.users():
            users.append({
                'name': user.name,
                'terminal': user.terminal,
                'host': user.host,
                'started': datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # SUID files
        suid_files = run_cmd("find / -perm -4000 -type f 2>/dev/null | head -20")
        
        # SELinux/AppArmor
        selinux = run_cmd("getenforce 2>/dev/null") or "N/A"
        apparmor = run_cmd("aa-status 2>/dev/null | head -1") or "N/A"
        
        return {
            'failed_logins': failed_logins.split('\n')[:20] if failed_logins else [],
            'logged_users': users,
            'suid_files': suid_files.split('\n')[:20] if suid_files else [],
            'selinux': selinux,
            'apparmor': apparmor
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== DOCKER ====================
def get_docker_info():
    """Informasi Docker"""
    try:
        # Check if docker is installed
        docker_version = run_cmd("docker --version 2>/dev/null")
        if not docker_version:
            return {'installed': False}
        
        # Containers
        containers = run_cmd("docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}|{{.Image}}'")
        container_list = []
        
        if containers:
            for line in containers.split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) == 4:
                        container_list.append({
                            'id': parts[0],
                            'name': parts[1],
                            'status': parts[2],
                            'image': parts[3]
                        })
        
        # Images
        images = run_cmd("docker images --format '{{.Repository}}:{{.Tag}}|{{.Size}}'")
        image_list = []
        
        if images:
            for line in images.split('\n'):
                if line and '|' in line:
                    parts = line.split('|')
                    image_list.append({
                        'name': parts[0],
                        'size': parts[1]
                    })
        
        return {
            'installed': True,
            'version': docker_version,
            'containers': container_list,
            'images': image_list
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== LOGS ====================
def get_logs_info():
    """Informasi logs"""
    try:
        logs = {
            'syslog': run_cmd("tail -50 /var/log/syslog 2>/dev/null").split('\n'),
            'auth': run_cmd("tail -50 /var/log/auth.log 2>/dev/null").split('\n'),
            'kern': run_cmd("tail -50 /var/log/kern.log 2>/dev/null").split('\n')
        }
        return logs
    except Exception as e:
        return {'error': str(e)}

# ==================== SERVER STATUS ====================
def get_server_status():
    """Status server lengkap"""
    try:
        # Running services
        services = []
        service_names = ['nginx', 'apache2', 'mysql', 'mariadb', 'postgresql', 'redis', 'php-fpm', 'ssh', 'docker', 'cron']
        
        for svc in service_names:
            status = run_cmd(f"systemctl is-active {svc} 2>/dev/null")
            if status == 'active':
                pid = run_cmd(f"systemctl show {svc} --property=MainPID --value")
                services.append({
                    'name': svc,
                    'status': 'running',
                    'pid': pid
                })
        
        # Listening ports with services
        listening_ports = []
        ports_output = run_cmd("ss -tulpn | grep LISTEN")
        if ports_output:
            for line in ports_output.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        addr_port = parts[4]
                        if ':' in addr_port:
                            port = addr_port.split(':')[-1]
                            process = parts[-1] if len(parts) > 5 else 'unknown'
                            listening_ports.append({
                                'port': port,
                                'process': process
                            })
        
        # System alerts
        alerts = []
        
        # Check CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            alerts.append({'level': 'critical', 'message': f'CPU usage critical: {cpu_percent:.1f}%'})
        elif cpu_percent > 80:
            alerts.append({'level': 'warning', 'message': f'CPU usage high: {cpu_percent:.1f}%'})
        
        # Check Memory
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            alerts.append({'level': 'critical', 'message': f'Memory usage critical: {mem.percent:.1f}%'})
        elif mem.percent > 80:
            alerts.append({'level': 'warning', 'message': f'Memory usage high: {mem.percent:.1f}%'})
        
        # Check Disk
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > 90:
                    alerts.append({'level': 'critical', 'message': f'Disk {part.mountpoint} critical: {usage.percent:.1f}%'})
                elif usage.percent > 80:
                    alerts.append({'level': 'warning', 'message': f'Disk {part.mountpoint} high: {usage.percent:.1f}%'})
            except:
                continue
        
        # Check failed services
        for svc in service_names:
            status = run_cmd(f"systemctl is-active {svc} 2>/dev/null")
            enabled = run_cmd(f"systemctl is-enabled {svc} 2>/dev/null")
            if enabled == 'enabled' and status != 'active':
                alerts.append({'level': 'critical', 'message': f'Service {svc} is down'})
        
        # OOM events
        oom_events = run_cmd("dmesg | grep -i 'out of memory' | tail -5")
        if oom_events:
            alerts.append({'level': 'critical', 'message': 'OOM (Out of Memory) events detected'})
        
        if not alerts:
            alerts.append({'level': 'success', 'message': 'All systems operational'})
        
        # Top processes
        top_procs = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                          key=lambda x: x.info.get('cpu_percent', 0), reverse=True)[:5]:
            try:
                top_procs.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except:
                continue
        
        # Network connections
        connections = psutil.net_connections(kind='inet')
        established = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        # Open ports count
        open_ports = len(set([c.laddr.port for c in connections if c.status == 'LISTEN']))
        
        return {
            'online': True,
            'services': services,
            'listening_ports': listening_ports[:20],  # Limit to 20
            'alerts': alerts,
            'top_processes': top_procs,
            'connections': established,
            'open_ports': open_ports
        }
    except Exception as e:
        return {'error': str(e), 'online': False}

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system')
def api_system():
    return jsonify(get_cached('system', get_system_info))

@app.route('/api/cpu')
def api_cpu():
    return jsonify(get_cached('cpu', get_cpu_info))

@app.route('/api/memory')
def api_memory():
    return jsonify(get_cached('memory', get_memory_info))

@app.route('/api/disk')
def api_disk():
    return jsonify(get_cached('disk', get_disk_info))

@app.route('/api/network')
def api_network():
    return jsonify(get_cached('network', get_network_info))

@app.route('/api/processes')
def api_processes():
    return jsonify(get_cached('processes', get_processes_info))

@app.route('/api/services')
def api_services():
    return jsonify(get_cached('services', get_services_info))

@app.route('/api/security')
def api_security():
    return jsonify(get_cached('security', get_security_info_enhanced))

@app.route('/api/gpu')
def api_gpu():
    return jsonify(get_cached('gpu', get_gpu_info))

@app.route('/api/process-list')
def api_process_list():
    return jsonify(get_process_list())

@app.route('/api/process-summary')
def api_process_summary():
    return jsonify(get_cached('process_summary', get_process_summary))

@app.route('/api/docker')
def api_docker():
    return jsonify(get_cached('docker', get_docker_info))

@app.route('/api/logs')
def api_logs():
    return jsonify(get_logs_info())

@app.route('/api/server-status')
def api_server_status():
    return jsonify(get_cached('server_status', get_server_status))

@app.route('/api/all')
def api_all():
    """Get all data at once"""
    return jsonify({
        'system': get_cached('system', get_system_info),
        'cpu': get_cached('cpu', get_cpu_info),
        'memory': get_cached('memory', get_memory_info),
        'gpu': get_cached('gpu', get_gpu_info),
        'disk': get_cached('disk', get_disk_info),
        'network': get_cached('network', get_network_info),
        'processes': get_cached('processes', get_processes_info),
        'process_summary': get_cached('process_summary', get_process_summary),
        'services': get_cached('services', get_services_info),
        'security': get_cached('security', get_security_info_enhanced),
        'docker': get_cached('docker', get_docker_info),
        'server_status': get_cached('server_status', get_server_status)
    })

@app.route('/api/storage/tree')
def api_storage_tree():
    path = request.args.get('path', '/')
    max_depth = int(request.args.get('depth', 2))
    return jsonify(get_directory_tree(path, max_depth))

@app.route('/api/storage/large-files')
def api_large_files():
    path = request.args.get('path', '/')
    min_size = int(request.args.get('min_size', 100))
    return jsonify(find_large_files(path, min_size))

@app.route('/api/storage/summary')
def api_storage_summary():
    return jsonify(get_cached('storage_summary', get_storage_summary))

@app.route('/api/network/traffic')
def api_network_traffic():
    return jsonify(get_network_traffic_details())

@app.route('/api/network/connections')
def api_network_connections():
    return jsonify(get_network_connections_detailed())

@app.route('/api/k8s/pods')
def api_k8s_pods():
    return jsonify(get_cached('k8s_pods', get_k8s_pods))

@app.route('/api/k8s/services')
def api_k8s_services():
    return jsonify(get_cached('k8s_services', get_k8s_services))

@app.route('/api/k8s/deployments')
def api_k8s_deployments():
    return jsonify(get_cached('k8s_deployments', get_k8s_deployments))

@app.route('/api/k8s/nodes')
def api_k8s_nodes():
    return jsonify(get_cached('k8s_nodes', get_k8s_nodes))

@app.route('/api/k8s/available')
def api_k8s_available():
    return jsonify({'available': is_k8s_available()})

@app.route('/api/version')
def api_version():
    return jsonify({'version': VERSION})

@app.route('/api/performance')
def api_performance():
    return jsonify(get_cached('performance', get_performance_metrics))

@app.route('/api/resource-limits')
def api_resource_limits():
    return jsonify(get_cached('resource_limits', get_resource_limits))

@app.route('/api/thermal')
def api_thermal():
    return jsonify(get_cached('thermal', get_thermal_power))

@app.route('/api/internet')
def api_internet():
    return jsonify(check_internet_connectivity())

if __name__ == '__main__':
    print("="*60)
    print("System Monitor Dashboard")
    print(f"Version: {VERSION}")
    print("Author: M. Nafiurohman")
    print("="*60)
    print(f"Starting server at: http://127.0.0.1:9999")
    print("Press Ctrl+C to stop")
    print("="*60)
    app.run(host='127.0.0.1', port=9999, debug=False)
