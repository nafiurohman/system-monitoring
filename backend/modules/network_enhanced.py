import psutil
import time

# Store previous network stats for rate calculation
_prev_net_io = {}
_prev_time = time.time()

def get_network_traffic_details():
    """Get detailed network traffic per interface"""
    global _prev_net_io, _prev_time
    
    current_io = psutil.net_io_counters(pernic=True)
    current_time = time.time()
    time_delta = current_time - _prev_time
    
    interfaces = []
    
    for iface, stats in current_io.items():
        # Calculate rates
        if iface in _prev_net_io and time_delta > 0:
            prev = _prev_net_io[iface]
            upload_rate = (stats.bytes_sent - prev.bytes_sent) / time_delta
            download_rate = (stats.bytes_recv - prev.bytes_recv) / time_delta
            packets_sent_rate = (stats.packets_sent - prev.packets_sent) / time_delta
            packets_recv_rate = (stats.packets_recv - prev.packets_recv) / time_delta
        else:
            upload_rate = download_rate = packets_sent_rate = packets_recv_rate = 0
        
        # Get interface addresses
        addrs = psutil.net_if_addrs().get(iface, [])
        ip_address = next((addr.address for addr in addrs if addr.family == 2), 'N/A')
        
        # Get interface status
        if_stats = psutil.net_if_stats().get(iface)
        is_up = if_stats.isup if if_stats else False
        speed = if_stats.speed if if_stats else 0
        
        interfaces.append({
            'name': iface,
            'ip': ip_address,
            'status': 'up' if is_up else 'down',
            'speed': f"{speed} Mbps" if speed > 0 else 'Unknown',
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'bytes_sent_human': format_bytes(stats.bytes_sent),
            'bytes_recv_human': format_bytes(stats.bytes_recv),
            'upload_rate': upload_rate,
            'download_rate': download_rate,
            'upload_rate_human': f"{format_bytes(upload_rate)}/s",
            'download_rate_human': f"{format_bytes(download_rate)}/s",
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv,
            'packets_sent_rate': int(packets_sent_rate),
            'packets_recv_rate': int(packets_recv_rate),
            'errors_in': stats.errin,
            'errors_out': stats.errout,
            'drops_in': stats.dropin,
            'drops_out': stats.dropout
        })
    
    # Update previous stats
    _prev_net_io = current_io
    _prev_time = current_time
    
    return interfaces

def get_network_connections_detailed():
    """Get detailed network connections"""
    connections = []
    
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                continue
            
            local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A'
            remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A'
            
            connections.append({
                'protocol': 'TCP' if conn.type == 1 else 'UDP',
                'local': local_addr,
                'remote': remote_addr,
                'status': conn.status,
                'pid': conn.pid or 'N/A'
            })
    except:
        pass
    
    return connections[:100]  # Limit to 100 connections

def format_bytes(bytes_val):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"
