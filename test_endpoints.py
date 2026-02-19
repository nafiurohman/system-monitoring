#!/usr/bin/env python3
"""
Test Script untuk System Monitor
Verifikasi semua endpoint dan fitur
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:9999"

def test_endpoint(name, endpoint):
    """Test single endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("System Monitor - Endpoint Testing")
    print("=" * 60)
    print()
    
    endpoints = [
        ("System Info", "/api/system"),
        ("CPU Info", "/api/cpu"),
        ("Memory Info", "/api/memory"),
        ("GPU Info", "/api/gpu"),
        ("Disk Info", "/api/disk"),
        ("Network Info", "/api/network"),
        ("Processes", "/api/processes"),
        ("Process List", "/api/process-list"),
        ("Process Summary", "/api/process-summary"),
        ("Services", "/api/services"),
        ("Security", "/api/security"),
        ("Docker", "/api/docker"),
        ("Logs", "/api/logs"),
        ("Server Status", "/api/server-status"),
        ("All Data", "/api/all"),
        ("Storage Summary", "/api/storage/summary"),
        ("Network Traffic", "/api/network/traffic"),
        ("Network Connections", "/api/network/connections"),
    ]
    
    results = []
    for name, endpoint in endpoints:
        result = test_endpoint(name, endpoint)
        results.append(result)
    
    print()
    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if sum(results) == len(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
