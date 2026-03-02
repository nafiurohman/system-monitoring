#!/usr/bin/env python3
"""
B-Monitor Backend Service

This is the core Flask application that serves monitoring data via a secure API.
"""

from flask import Flask, render_template, jsonify, request
import psutil
import platform
import socket
import os
import time
import json
import logging
import configparser
from functools import wraps

# Import modular components
from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.gpu import get_gpu_info
from modules.security import get_security_info
from modules.processes import get_process_list, get_process_summary
from modules.storage import get_storage_summary
from modules.network_enhanced import get_network_traffic_details, get_network_connections_detailed
from modules.performance import get_performance_metrics

# --- Configuration ---
VERSION = "bmonitor-0.1.0"
CACHE_TTL = 1.0  # Cache Time-To-Live in seconds

CONFIG_PATH = "/opt/bmonitor/config/app.ini"
DEFAULT_PORT = 9999

def load_port():
    """Load port from config file, fallback to default."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        return config.getint("server", "port", fallback=DEFAULT_PORT)
    return DEFAULT_PORT

# --- App Initialization ---
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Disable default Flask logging to keep output clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- Caching Mechanism ---
cache = {}
cache_time = {}

def get_cached(key, func, *args, **kwargs):
    """Simple Time-To-Live (TTL) cache."""
    now = time.time()
    if key in cache and (now - cache_time.get(key, 0)) < CACHE_TTL:
        return cache[key]

    data = func(*args, **kwargs)
    cache[key] = data
    cache_time[key] = now
    return data

# --- Authentication (Placeholder) ---
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# --- API Endpoints ---

@app.route('/')
def index():
    """Serves the main frontend (placeholder)."""
    return "B-Monitor Backend is running. Frontend is not yet integrated."

@app.route('/api/v1/all')
@auth_required
def api_all():
    """Get all monitoring data at once."""
    all_data = {
        'system': get_cached('system', lambda: {'hostname': socket.gethostname(), 'os': f"{platform.system()} {platform.release()}"}),
        'cpu': get_cached('cpu', get_cpu_info),
        'memory': get_cached('memory', get_memory_info),
        'gpu': get_cached('gpu', get_gpu_info),
        'storage': get_cached('storage', get_storage_summary),
        'network_traffic': get_cached('network_traffic', get_network_traffic_details),
        'network_connections': get_cached('network_connections', get_network_connections_detailed),
        'processes': get_cached('processes', get_process_summary),
        'performance': get_cached('performance', get_performance_metrics),
        'security': get_cached('security', get_security_info),
    }
    return jsonify({"status": "success", "data": all_data})

# --- Individual API Endpoints ---

@app.route('/api/v1/cpu')
@auth_required
def api_cpu():
    return jsonify(get_cached('cpu', get_cpu_info))

@app.route('/api/v1/memory')
@auth_required
def api_memory():
    return jsonify(get_cached('memory', get_memory_info))

@app.route('/api/v1/storage')
@auth_required
def api_storage():
    return jsonify(get_cached('storage', get_storage_summary))

@app.route('/api/v1/network')
@auth_required
def api_network():
    data = {
        'traffic': get_cached('network_traffic', get_network_traffic_details),
        'connections': get_cached('network_connections', get_network_connections_detailed)
    }
    return jsonify(data)

@app.route('/api/v1/processes')
@auth_required
def api_processes():
    return jsonify(get_cached('process_list', get_process_list))

# --- Main Execution ---
if __name__ == '__main__':
    port = load_port()
    app.run(host='0.0.0.0', port=port, debug=False)
