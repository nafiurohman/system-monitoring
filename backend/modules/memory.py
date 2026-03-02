"""
Memory Monitoring Module - High Performance
Author: M. Nafiurohman
"""

import psutil
from utils.helpers import run_cmd, IS_WINDOWS

def get_memory_info():
    """Get detailed memory information with breakdown"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # ZRAM detection (Linux only)
        zram_devices = []
        if not IS_WINDOWS:
            try:
                zram_info = run_cmd("zramctl --output NAME,DISKSIZE,DATA,COMPR,TOTAL --raw --noheadings")
                if zram_info:
                    for line in zram_info.split('\n'):
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 5:
                                zram_devices.append({
                                    'device': parts[0],
                                    'disksize': parts[1],
                                    'data': parts[2],
                                    'compr': parts[3],
                                    'total': parts[4]
                                })
            except:
                pass
        
        # Memory breakdown
        breakdown = {
            'used': mem.used,
            'free': mem.free,
            'available': mem.available,
            'buffers': getattr(mem, 'buffers', 0),
            'cached': getattr(mem, 'cached', 0),
            'shared': getattr(mem, 'shared', 0),
            'active': getattr(mem, 'active', 0),
            'inactive': getattr(mem, 'inactive', 0),
            'wired': getattr(mem, 'wired', 0)
        }
        
        return {
            'ram': {
                'total': mem.total,
                'used': mem.used,
                'free': mem.free,
                'available': mem.available,
                'percent': round(mem.percent, 1),
                'buffers': getattr(mem, 'buffers', 0),
                'cached': getattr(mem, 'cached', 0),
                'shared': getattr(mem, 'shared', 0),
                'active': getattr(mem, 'active', 0),
                'inactive': getattr(mem, 'inactive', 0)
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': round(swap.percent, 1),
                'sin': swap.sin,
                'sout': swap.sout
            },
            'zram': zram_devices,
            'breakdown': breakdown
        }
    except Exception as e:
        return {'error': str(e)}
