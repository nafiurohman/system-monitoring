# API Documentation

System Monitor Dashboard provides RESTful API endpoints for programmatic access to system information.

## Base URL

```
http://127.0.0.1:9999
```

## Endpoints

### 1. System Information

**GET** `/api/system`

Returns system identity and basic information.

**Response:**
```json
{
  "hostname": "server01",
  "fqdn": "server01.example.com",
  "os": "Linux 5.15.0",
  "kernel": "5.15.0-91-generic",
  "architecture": "x86_64",
  "virtualization": "kvm",
  "uptime": "5 days, 3:24:15",
  "boot_time": "2024-02-13 10:30:00"
}
```

### 2. CPU Information

**GET** `/api/cpu`

Returns CPU usage and details.

**Response:**
```json
{
  "model": "Intel Core i7-9700K",
  "cores": 8,
  "threads": 8,
  "frequency": {
    "current": 3600.0,
    "min": 800.0,
    "max": 4900.0
  },
  "usage_total": 25.5,
  "usage_per_core": [20.1, 30.5, 25.0, ...],
  "load_average": {
    "1min": 1.25,
    "5min": 1.50,
    "15min": 1.75
  },
  "temperature": 45.0
}
```

### 3. Memory Information

**GET** `/api/memory`

Returns RAM and SWAP usage.

**Response:**
```json
{
  "ram": {
    "total": 16777216000,
    "used": 8388608000,
    "free": 8388608000,
    "percent": 50.0
  },
  "swap": {
    "total": 4294967296,
    "used": 0,
    "free": 4294967296,
    "percent": 0.0
  }
}
```

### 4. Disk Information

**GET** `/api/disk`

Returns disk partitions and usage.

**Response:**
```json
{
  "partitions": [
    {
      "device": "/dev/sda1",
      "mountpoint": "/",
      "fstype": "ext4",
      "total": 107374182400,
      "used": 53687091200,
      "free": 53687091200,
      "percent": 50.0,
      "smart_status": "PASSED"
    }
  ]
}
```

### 5. Network Information

**GET** `/api/network`

Returns network interfaces and traffic.

**Response:**
```json
{
  "interfaces": [
    {
      "name": "eth0",
      "ip": "192.168.1.100",
      "mac": "00:11:22:33:44:55",
      "status": "UP",
      "bytes_sent": 1073741824,
      "bytes_recv": 2147483648
    }
  ],
  "public_ip": "203.0.113.1",
  "connections": {
    "total": 150,
    "established": 45
  }
}
```

### 6. Process Information

**GET** `/api/processes`

Returns running processes.

**Response:**
```json
{
  "total": 250,
  "top_cpu": [
    {
      "pid": 1234,
      "name": "python3",
      "cpu_percent": 15.5,
      "memory_percent": 2.3
    }
  ],
  "top_memory": [...]
}
```

### 7. Services Information

**GET** `/api/services`

Returns system services status.

**Response:**
```json
{
  "services": [
    {
      "name": "nginx",
      "status": "active",
      "enabled": "enabled",
      "pid": "1234"
    }
  ]
}
```

### 8. Security Information

**GET** `/api/security`

Returns security-related information.

**Response:**
```json
{
  "logged_users": [
    {
      "name": "admin",
      "terminal": "pts/0",
      "host": "192.168.1.50",
      "started": "2024-02-18 10:00:00"
    }
  ],
  "failed_logins": [...]
}
```

### 9. Docker Information

**GET** `/api/docker`

Returns Docker containers and images.

**Response:**
```json
{
  "installed": true,
  "containers": [
    {
      "id": "abc123",
      "name": "web-app",
      "status": "Up 2 hours",
      "image": "nginx:latest"
    }
  ],
  "images": [...]
}
```

### 10. Logs

**GET** `/api/logs`

Returns system logs.

**Response:**
```json
{
  "syslog": ["log line 1", "log line 2", ...],
  "auth": [...],
  "kern": [...]
}
```

### 11. All Data

**GET** `/api/all`

Returns all monitoring data in one request.

**Response:**
```json
{
  "system": {...},
  "cpu": {...},
  "memory": {...},
  "disk": {...},
  "network": {...},
  "processes": {...},
  "services": {...},
  "security": {...},
  "docker": {...}
}
```

## Usage Examples

### cURL

```bash
# Get system information
curl http://127.0.0.1:9999/api/system

# Get all data
curl http://127.0.0.1:9999/api/all
```

### Python

```python
import requests

response = requests.get('http://127.0.0.1:9999/api/cpu')
data = response.json()
print(f"CPU Usage: {data['usage_total']}%")
```

### JavaScript

```javascript
fetch('http://127.0.0.1:9999/api/memory')
  .then(response => response.json())
  .then(data => {
    console.log(`Memory Usage: ${data.ram.percent}%`);
  });
```

## Rate Limiting

- No rate limiting by default
- Data is cached for 2 seconds (TTL)
- Recommended polling interval: 3-5 seconds

## Error Responses

All endpoints return JSON with error information if something goes wrong:

```json
{
  "error": "Error message description"
}
```

## Notes

- All byte values are in bytes (use formatBytes function to convert)
- All percentages are in range 0-100
- Timestamps are in format: YYYY-MM-DD HH:MM:SS
- Some endpoints require root/sudo access for full information

---

**Author:** M. Nafiurohman  
**Contact:** nafiurohman25@gmail.com
