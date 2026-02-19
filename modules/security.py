"""
Enhanced Security Monitoring Module
Author: M. Nafiurohman
"""

import psutil
from datetime import datetime
from utils.helpers import run_cmd, IS_WINDOWS

def get_security_info():
    """Enhanced security monitoring"""
    try:
        security_data = {
            'firewall': get_firewall_status(),
            'antivirus': get_antivirus_status(),
            'open_ports': get_open_ports_detailed(),
            'failed_logins': get_failed_logins(),
            'logged_users': get_logged_users(),
            'suspicious_processes': get_suspicious_processes(),
            'security_score': 0
        }
        
        # Calculate security score
        score = 100
        if not security_data['firewall']['enabled']:
            score -= 30
        if not security_data['antivirus']['enabled']:
            score -= 20
        if len(security_data['open_ports']) > 10:
            score -= 10
        if len(security_data['failed_logins']) > 5:
            score -= 10
        
        security_data['security_score'] = max(0, score)
        return security_data
    except Exception as e:
        return {'error': str(e)}

def get_firewall_status():
    """Get firewall status and rules"""
    if IS_WINDOWS:
        status = run_cmd("netsh advfirewall show allprofiles state")
        enabled = "ON" in status
        return {
            'enabled': enabled,
            'type': 'Windows Defender Firewall',
            'status': 'Active' if enabled else 'Inactive'
        }
    else:
        ufw_status = run_cmd("ufw status")
        iptables_rules = run_cmd("iptables -L -n | wc -l")
        
        if "active" in ufw_status.lower():
            return {
                'enabled': True,
                'type': 'UFW',
                'status': 'Active',
                'rules_count': len(ufw_status.split('\n'))
            }
        elif iptables_rules and int(iptables_rules) > 10:
            return {
                'enabled': True,
                'type': 'iptables',
                'status': 'Active',
                'rules_count': int(iptables_rules)
            }
        else:
            return {
                'enabled': False,
                'type': 'None',
                'status': 'Inactive'
            }

def get_antivirus_status():
    """Get antivirus/defender status"""
    if IS_WINDOWS:
        defender = run_cmd("powershell Get-MpComputerStatus | Select-String 'AntivirusEnabled'")
        enabled = "True" in defender
        return {
            'enabled': enabled,
            'name': 'Windows Defender',
            'status': 'Active' if enabled else 'Inactive'
        }
    else:
        # Check for ClamAV
        clamav = run_cmd("systemctl is-active clamav-daemon")
        if clamav == "active":
            return {
                'enabled': True,
                'name': 'ClamAV',
                'status': 'Active'
            }
        return {
            'enabled': False,
            'name': 'None',
            'status': 'Not Installed'
        }

def get_open_ports_detailed():
    """Get detailed open ports with protocol and risk level"""
    ports = []
    try:
        connections = psutil.net_connections(kind='inet')
        
        # Dangerous ports list
        dangerous_ports = {
            21: 'FTP', 23: 'Telnet', 135: 'RPC', 139: 'NetBIOS',
            445: 'SMB', 3389: 'RDP', 5900: 'VNC'
        }
        
        seen_ports = set()
        
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr:
                port = conn.laddr.port
                
                # Skip duplicates
                if port in seen_ports:
                    continue
                seen_ports.add(port)
                
                # Determine protocol
                protocol = 'TCP' if conn.type == 1 else 'UDP'
                
                risk = 'Low'
                if port in dangerous_ports:
                    risk = 'High'
                elif port < 1024:
                    risk = 'Medium'
                
                service = dangerous_ports.get(port, get_service_name(port))
                
                # Get process name
                process_name = 'Unknown'
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        process_name = proc.name()
                    except:
                        pass
                
                ports.append({
                    'port': port,
                    'protocol': protocol,
                    'service': service,
                    'process': process_name,
                    'risk': risk,
                    'address': conn.laddr.ip
                })
        
        return sorted(ports, key=lambda x: x['port'])
    except Exception as e:
        return []

def get_service_name(port):
    """Get service name for port"""
    common_ports = {
        22: 'SSH', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL',
        5432: 'PostgreSQL', 6379: 'Redis', 27017: 'MongoDB',
        8080: 'HTTP-Alt', 9000: 'PHP-FPM', 9999: 'Monitor'
    }
    return common_ports.get(port, 'Unknown')

def get_failed_logins():
    """Get failed login attempts"""
    if IS_WINDOWS:
        cmd = "wevtutil qe Security /c:20 /rd:true /f:text /q:\"*[System[(EventID=4625)]]\""
        result = run_cmd(cmd)
        return result.split('\n')[:20] if result else []
    else:
        result = run_cmd("grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -20")
        return result.split('\n') if result else []

def get_logged_users():
    """Get currently logged users"""
    users = []
    for user in psutil.users():
        users.append({
            'name': user.name,
            'terminal': user.terminal,
            'host': user.host,
            'started': datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
        })
    return users

def get_suspicious_processes():
    """Detect suspicious processes"""
    suspicious = []
    suspicious_names = ['nc', 'netcat', 'nmap', 'mimikatz', 'psexec']
    
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if any(sus in proc.info['name'].lower() for sus in suspicious_names):
                suspicious.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'user': proc.info['username']
                })
        except:
            continue
    
    return suspicious
