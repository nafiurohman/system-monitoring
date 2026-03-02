"""
Utility helpers for cross-platform support
Author: M. Nafiurohman
"""

import platform
import subprocess

IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

def run_cmd(cmd, timeout=5):
    """Execute command with platform detection"""
    try:
        if IS_WINDOWS:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""

def get_cpu_name():
    """Get CPU name cross-platform"""
    if IS_WINDOWS:
        try:
            import wmi
            w = wmi.WMI()
            for processor in w.Win32_Processor():
                return processor.Name.strip()
        except:
            pass
        
        # Fallback to wmic
        result = run_cmd("wmic cpu get name")
        if result:
            lines = result.split('\n')
            for line in lines:
                if line.strip() and 'Name' not in line:
                    return line.strip()
        
        # Last fallback
        import platform
        return platform.processor() or "Unknown CPU"
    else:
        result = run_cmd("lscpu | grep 'Model name' | cut -d':' -f2 | xargs")
        return result if result else "Unknown CPU"
