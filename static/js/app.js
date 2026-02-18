// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Update page
        const page = item.dataset.page;
        document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
        document.getElementById(`${page}-page`).classList.add('active');
        
        // Update title
        const title = item.querySelector('span').textContent;
        document.getElementById('currentPageTitle').textContent = title;
        
        // Load page data
        loadPageData(page);
    });
});

// Charts
let cpuChart, memChart, netChart;
let cpuHistory = [];
let memHistory = [];
let netSentHistory = [];
let netRecvHistory = [];
const maxDataPoints = 30;

function initCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(15, 31, 58, 0.9)',
                titleColor: '#e8f0ff',
                bodyColor: '#a8c5e8',
                borderColor: 'rgba(46, 90, 143, 0.5)',
                borderWidth: 1,
                padding: 10,
                displayColors: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                grid: { color: 'rgba(46, 90, 143, 0.2)' },
                ticks: { color: '#a8c5e8', font: { size: 11 } }
            },
            x: {
                grid: { color: 'rgba(46, 90, 143, 0.2)' },
                ticks: { color: '#a8c5e8', font: { size: 11 } }
            }
        },
        animation: {
            duration: 500
        }
    };

    // CPU Chart
    const cpuCtx = document.getElementById('cpuChart');
    if (cpuCtx) {
        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: '#4a8fd8',
                    backgroundColor: 'rgba(74, 143, 216, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: chartOptions
        });
    }

    // Memory Chart
    const memCtx = document.getElementById('memChart');
    if (memCtx) {
        memChart = new Chart(memCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory %',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: chartOptions
        });
    }

    // Network Chart
    const netCtx = document.getElementById('netChart');
    if (netCtx) {
        netChart = new Chart(netCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Sent (MB)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Received (MB)',
                        data: [],
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...chartOptions,
                plugins: { 
                    legend: { 
                        display: true, 
                        labels: { color: '#a8c5e8', font: { size: 11 } } 
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(15, 31, 58, 0.9)',
                        titleColor: '#e8f0ff',
                        bodyColor: '#a8c5e8',
                        borderColor: 'rgba(46, 90, 143, 0.5)',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                scales: {
                    ...chartOptions.scales,
                    y: { ...chartOptions.scales.y, max: undefined }
                },
                interaction: {
                    mode: 'index',
                    intersect: false,
                }
            }
        });
    }
}

function updateCharts(cpuUsage, memUsage, netSent, netRecv) {
    const now = new Date().toLocaleTimeString();
    
    // Update CPU Chart
    if (cpuChart) {
        cpuHistory.push(cpuUsage);
        if (cpuHistory.length > maxDataPoints) cpuHistory.shift();
        
        cpuChart.data.labels = Array(cpuHistory.length).fill('').map((_, i) => '');
        cpuChart.data.datasets[0].data = cpuHistory;
        cpuChart.update('none');
    }
    
    // Update Memory Chart
    if (memChart) {
        memHistory.push(memUsage);
        if (memHistory.length > maxDataPoints) memHistory.shift();
        
        memChart.data.labels = Array(memHistory.length).fill('').map((_, i) => '');
        memChart.data.datasets[0].data = memHistory;
        memChart.update('none');
    }
    
    // Update Network Chart
    if (netChart) {
        netSentHistory.push(netSent / 1024 / 1024); // Convert to MB
        netRecvHistory.push(netRecv / 1024 / 1024);
        
        if (netSentHistory.length > maxDataPoints) {
            netSentHistory.shift();
            netRecvHistory.shift();
        }
        
        netChart.data.labels = Array(netSentHistory.length).fill('').map((_, i) => '');
        netChart.data.datasets[0].data = netSentHistory;
        netChart.data.datasets[1].data = netRecvHistory;
        netChart.update('none');
    }
}

// Export logs to JSON
function exportLogs(type) {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logs = data[type] || [];
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}-logs-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
}
function copyAccount() {
    const accountNumber = document.getElementById('accountNumber').textContent;
    navigator.clipboard.writeText(accountNumber).then(() => {
        const btn = document.querySelector('.copy-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);
    });
}

// Format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format number
function formatNumber(num) {
    return num.toFixed(2);
}

// Update server time
function updateServerTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('serverTime').textContent = timeStr;
}

// Load all data
async function loadAllData() {
    try {
        const response = await fetch('/api/all');
        const data = await response.json();
        
        // Always update overview if it's the active page
        const activePage = document.querySelector('.page-content.active');
        if (activePage) {
            const pageId = activePage.id.replace('-page', '');
            
            if (pageId === 'overview') {
                updateOverview(data);
            } else if (pageId === 'server-status') {
                updateServerStatus(data);
            }
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update Overview
function updateOverview(data) {
    // System info
    const sysCard = document.querySelector('#overview-page .grid-4 .card:nth-child(1) .card-body');
    if (data.system && sysCard) {
        sysCard.innerHTML = `
            <div class="info-row">
                <span class="label">Hostname</span>
                <span class="value">${data.system.hostname || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">OS</span>
                <span class="value">${data.system.os || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Kernel</span>
                <span class="value">${data.system.kernel || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Uptime</span>
                <span class="value">${data.system.uptime || '-'}</span>
            </div>
        `;
    }
    
    // CPU
    const cpuCard = document.querySelector('#overview-page .grid-4 .card:nth-child(2) .card-body');
    if (data.cpu && cpuCard) {
        const cpuUsage = data.cpu.usage_total || 0;
        let color = '#2e5a8f';
        if (cpuUsage > 80) color = '#ef4444';
        else if (cpuUsage > 60) color = '#f59e0b';
        
        cpuCard.innerHTML = `
            <div class="metric-medium">
                <div class="metric-value">${cpuUsage.toFixed(1)}%</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${cpuUsage}%; background: linear-gradient(90deg, ${color}, ${color}dd)"></div>
            </div>
            <div class="info-row">
                <span class="label">Load</span>
                <span class="value">${data.cpu.load_average ? data.cpu.load_average['1min'].toFixed(2) : '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Temp</span>
                <span class="value">${data.cpu.temperature ? data.cpu.temperature.toFixed(1) + '°C' : 'N/A'}</span>
            </div>
        `;
    }
    
    // Memory
    const memCard = document.querySelector('#overview-page .grid-4 .card:nth-child(3) .card-body');
    if (data.memory && data.memory.ram && memCard) {
        const memPercent = data.memory.ram.percent || 0;
        let color = '#2e5a8f';
        if (memPercent > 80) color = '#ef4444';
        else if (memPercent > 60) color = '#f59e0b';
        
        memCard.innerHTML = `
            <div class="metric-medium">
                <div class="metric-value">${memPercent.toFixed(1)}%</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${memPercent}%; background: linear-gradient(90deg, ${color}, ${color}dd)"></div>
            </div>
            <div class="info-row">
                <span class="label">Used</span>
                <span class="value">${formatBytes(data.memory.ram.used)}</span>
            </div>
            <div class="info-row">
                <span class="label">Free</span>
                <span class="value">${formatBytes(data.memory.ram.free)}</span>
            </div>
        `;
    }
    
    // Disk
    const diskCard = document.querySelector('#overview-page .grid-4 .card:nth-child(4) .card-body');
    if (data.disk && data.disk.partitions && data.disk.partitions.length > 0 && diskCard) {
        const rootPart = data.disk.partitions.find(p => p.mountpoint === '/') || data.disk.partitions[0];
        const diskPercent = rootPart.percent || 0;
        let color = '#2e5a8f';
        if (diskPercent > 80) color = '#ef4444';
        else if (diskPercent > 60) color = '#f59e0b';
        
        diskCard.innerHTML = `
            <div class="metric-medium">
                <div class="metric-value">${diskPercent.toFixed(1)}%</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${diskPercent}%; background: linear-gradient(90deg, ${color}, ${color}dd)"></div>
            </div>
            <div class="info-row">
                <span class="label">Used</span>
                <span class="value">${formatBytes(rootPart.used)}</span>
            </div>
            <div class="info-row">
                <span class="label">Free</span>
                <span class="value">${formatBytes(rootPart.free)}</span>
            </div>
        `;
    }
    
    // Update charts
    if (data.cpu && data.memory && data.network) {
        let totalSent = 0, totalRecv = 0;
        if (data.network.interfaces) {
            data.network.interfaces.forEach(iface => {
                if (iface.name !== 'lo') {
                    totalSent += iface.bytes_sent || 0;
                    totalRecv += iface.bytes_recv || 0;
                }
            });
        }
        updateCharts(
            data.cpu.usage_total || 0,
            data.memory.ram.percent || 0,
            totalSent,
            totalRecv
        );
    }
}

// Update Server Status
function updateServerStatus(data) {
    if (!data.server_status) return;
    
    const status = data.server_status;
    
    // Server online status
    const statusIcon = document.getElementById('server-online-status');
    const statusText = document.getElementById('server-status-text');
    if (status.online) {
        statusIcon.className = 'status-icon text-success';
        statusText.textContent = 'Online';
    } else {
        statusIcon.className = 'status-icon text-danger';
        statusText.textContent = 'Offline';
    }
    
    // Uptime
    if (data.system) {
        document.getElementById('status-uptime').textContent = data.system.uptime || '-';
    }
    
    // Open ports
    document.getElementById('status-ports').textContent = status.open_ports || 0;
    
    // Connections
    document.getElementById('status-connections').textContent = status.connections || 0;
    
    // Running services
    const servicesDiv = document.getElementById('status-services');
    servicesDiv.innerHTML = '';
    if (status.services && status.services.length > 0) {
        status.services.forEach(svc => {
            const item = document.createElement('div');
            item.className = 'service-item';
            item.innerHTML = `
                <div class="service-name">${svc.name}</div>
                <div class="service-status">
                    <span class="status-badge status-active">Running</span>
                    <span style="font-size: 11px; color: var(--text-secondary);">PID: ${svc.pid}</span>
                </div>
            `;
            servicesDiv.appendChild(item);
        });
    } else {
        servicesDiv.innerHTML = '<div class="loading">No running services</div>';
    }
    
    // Listening ports
    const portsDiv = document.getElementById('status-listening-ports');
    portsDiv.innerHTML = '';
    if (status.listening_ports && status.listening_ports.length > 0) {
        status.listening_ports.forEach(port => {
            const item = document.createElement('div');
            item.className = 'port-item';
            item.innerHTML = `
                <span class="port-number">${port.port}</span>
                <span class="port-service">${port.process}</span>
            `;
            portsDiv.appendChild(item);
        });
    } else {
        portsDiv.innerHTML = '<div class="loading">No listening ports</div>';
    }
    
    // Resource usage
    if (data.cpu) {
        const cpuPercent = data.cpu.usage_total || 0;
        document.getElementById('status-cpu-bar').style.width = cpuPercent + '%';
        document.getElementById('status-cpu-text').textContent = cpuPercent.toFixed(1) + '%';
        
        const cpuBar = document.getElementById('status-cpu-bar');
        if (cpuPercent > 80) cpuBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        else if (cpuPercent > 60) cpuBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        else cpuBar.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }
    
    if (data.memory && data.memory.ram) {
        const memPercent = data.memory.ram.percent || 0;
        document.getElementById('status-mem-bar').style.width = memPercent + '%';
        document.getElementById('status-mem-text').textContent = memPercent.toFixed(1) + '%';
        
        const memBar = document.getElementById('status-mem-bar');
        if (memPercent > 80) memBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        else if (memPercent > 60) memBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        else memBar.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }
    
    if (data.disk && data.disk.partitions && data.disk.partitions.length > 0) {
        const rootPart = data.disk.partitions.find(p => p.mountpoint === '/') || data.disk.partitions[0];
        const diskPercent = rootPart.percent || 0;
        document.getElementById('status-disk-bar').style.width = diskPercent + '%';
        document.getElementById('status-disk-text').textContent = diskPercent.toFixed(1) + '%';
        
        const diskBar = document.getElementById('status-disk-bar');
        if (diskPercent > 80) diskBar.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        else if (diskPercent > 60) diskBar.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        else diskBar.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    }
    
    // Alerts
    const alertsDiv = document.getElementById('status-alerts');
    alertsDiv.innerHTML = '';
    if (status.alerts && status.alerts.length > 0) {
        status.alerts.forEach(alert => {
            const item = document.createElement('div');
            item.className = `alert-item ${alert.level}`;
            item.textContent = alert.message;
            alertsDiv.appendChild(item);
        });
    } else {
        alertsDiv.innerHTML = '<div class="alert-item success">All systems operational</div>';
    }
    
    // Top processes
    const procsDiv = document.getElementById('status-top-processes');
    procsDiv.innerHTML = '';
    if (status.top_processes && status.top_processes.length > 0) {
        status.top_processes.forEach(proc => {
            const item = document.createElement('div');
            item.className = 'process-item';
            item.innerHTML = `
                <span class="process-name">${proc.name} (${proc.pid})</span>
                <span class="process-value">CPU: ${proc.cpu ? proc.cpu.toFixed(1) : '0.0'}%</span>
            `;
            procsDiv.appendChild(item);
        });
    } else {
        procsDiv.innerHTML = '<div class="loading">No processes</div>';
    }
}

// Update Hardware
function updateHardware(data) {
    // CPU Details
    if (data.cpu) {
        const cpuDiv = document.getElementById('hardware-cpu');
        cpuDiv.innerHTML = `
            <div class="info-row">
                <span class="label">Model</span>
                <span class="value">${data.cpu.model || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Cores</span>
                <span class="value">${data.cpu.cores || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Threads</span>
                <span class="value">${data.cpu.threads || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Frequency</span>
                <span class="value">${data.cpu.frequency ? data.cpu.frequency.current.toFixed(2) + ' MHz' : '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Cache Size</span>
                <span class="value">${data.cpu.cache_size || '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Temperature</span>
                <span class="value">${data.cpu.temperature ? data.cpu.temperature.toFixed(1) + '°C' : 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="label">Load Average (1m)</span>
                <span class="value">${data.cpu.load_average ? data.cpu.load_average['1min'].toFixed(2) : '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Load Average (5m)</span>
                <span class="value">${data.cpu.load_average ? data.cpu.load_average['5min'].toFixed(2) : '-'}</span>
            </div>
            <div class="info-row">
                <span class="label">Load Average (15m)</span>
                <span class="value">${data.cpu.load_average ? data.cpu.load_average['15min'].toFixed(2) : '-'}</span>
            </div>
        `;
    }
    
    // Memory Details
    if (data.memory) {
        const memDiv = document.getElementById('hardware-memory');
        let zramHtml = '';
        
        if (data.memory.zram && data.memory.zram.length > 0) {
            zramHtml = '<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--glass-border);">';
            zramHtml += '<div style="font-weight: 600; margin-bottom: 10px; color: var(--text-primary);">ZRAM Devices</div>';
            data.memory.zram.forEach(zram => {
                zramHtml += `
                    <div class="info-row">
                        <span class="label">${zram.device}</span>
                        <span class="value">${zram.disksize}</span>
                    </div>
                `;
            });
            zramHtml += '</div>';
        }
        
        memDiv.innerHTML = `
            <div class="info-row">
                <span class="label">Total RAM</span>
                <span class="value">${formatBytes(data.memory.ram.total)}</span>
            </div>
            <div class="info-row">
                <span class="label">Used RAM</span>
                <span class="value">${formatBytes(data.memory.ram.used)}</span>
            </div>
            <div class="info-row">
                <span class="label">Free RAM</span>
                <span class="value">${formatBytes(data.memory.ram.free)}</span>
            </div>
            <div class="info-row">
                <span class="label">Available</span>
                <span class="value">${formatBytes(data.memory.ram.available)}</span>
            </div>
            <div class="info-row">
                <span class="label">Buffers</span>
                <span class="value">${formatBytes(data.memory.ram.buffers)}</span>
            </div>
            <div class="info-row">
                <span class="label">Cached</span>
                <span class="value">${formatBytes(data.memory.ram.cached)}</span>
            </div>
            <div class="info-row">
                <span class="label">Swap Total</span>
                <span class="value">${formatBytes(data.memory.swap.total)}</span>
            </div>
            <div class="info-row">
                <span class="label">Swap Used</span>
                <span class="value">${formatBytes(data.memory.swap.used)}</span>
            </div>
            ${zramHtml}
        `;
    }
    
    // Disk Details
    if (data.disk && data.disk.partitions) {
        const diskDiv = document.getElementById('hardware-disk');
        diskDiv.innerHTML = '';
        
        data.disk.partitions.forEach(part => {
            const item = document.createElement('div');
            item.style.marginBottom = '20px';
            item.innerHTML = `
                <div class="disk-header">
                    <span class="disk-path">${part.mountpoint}</span>
                    <span class="disk-usage">${part.percent.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${part.percent}%"></div>
                </div>
                <div class="info-row">
                    <span class="label">Device</span>
                    <span class="value">${part.device}</span>
                </div>
                <div class="info-row">
                    <span class="label">Filesystem</span>
                    <span class="value">${part.fstype}</span>
                </div>
                <div class="info-row">
                    <span class="label">Total</span>
                    <span class="value">${formatBytes(part.total)}</span>
                </div>
                <div class="info-row">
                    <span class="label">Used</span>
                    <span class="value">${formatBytes(part.used)}</span>
                </div>
                <div class="info-row">
                    <span class="label">Free</span>
                    <span class="value">${formatBytes(part.free)}</span>
                </div>
                <div class="info-row">
                    <span class="label">SMART Status</span>
                    <span class="value">${part.smart_status}</span>
                </div>
            `;
            diskDiv.appendChild(item);
        });
    }
}

// Update Network
function updateNetwork(data) {
    if (!data.network) return;
    
    // Interfaces
    const interfacesDiv = document.getElementById('network-interfaces');
    interfacesDiv.innerHTML = '';
    
    if (data.network.interfaces) {
        data.network.interfaces.forEach(iface => {
            const item = document.createElement('div');
            item.style.marginBottom = '20px';
            item.innerHTML = `
                <div class="disk-header">
                    <span class="disk-path">${iface.name}</span>
                    <span class="status-badge ${iface.status === 'UP' ? 'status-active' : 'status-inactive'}">${iface.status}</span>
                </div>
                <div class="info-row">
                    <span class="label">IP Address</span>
                    <span class="value">${iface.ip || 'N/A'}</span>
                </div>
                <div class="info-row">
                    <span class="label">MAC Address</span>
                    <span class="value">${iface.mac || 'N/A'}</span>
                </div>
                <div class="info-row">
                    <span class="label">Link Speed</span>
                    <span class="value">${iface.link_speed}</span>
                </div>
                <div class="info-row">
                    <span class="label">Bytes Sent</span>
                    <span class="value">${formatBytes(iface.bytes_sent)}</span>
                </div>
                <div class="info-row">
                    <span class="label">Bytes Received</span>
                    <span class="value">${formatBytes(iface.bytes_recv)}</span>
                </div>
                <div class="info-row">
                    <span class="label">Packets Sent</span>
                    <span class="value">${iface.packets_sent}</span>
                </div>
                <div class="info-row">
                    <span class="label">Packets Received</span>
                    <span class="value">${iface.packets_recv}</span>
                </div>
                <div class="info-row">
                    <span class="label">Errors</span>
                    <span class="value">In: ${iface.errin} / Out: ${iface.errout}</span>
                </div>
            `;
            interfacesDiv.appendChild(item);
        });
    }
    
    // Connections
    const connectionsDiv = document.getElementById('network-connections');
    if (data.network.connections) {
        connectionsDiv.innerHTML = `
            <div class="info-row">
                <span class="label">Total Connections</span>
                <span class="value">${data.network.connections.total}</span>
            </div>
            <div class="info-row">
                <span class="label">Established</span>
                <span class="value">${data.network.connections.established}</span>
            </div>
            <div class="info-row">
                <span class="label">Public IP</span>
                <span class="value">${data.network.public_ip}</span>
            </div>
        `;
    }
    
    // Firewall
    const firewallDiv = document.getElementById('network-firewall');
    if (data.network.firewall) {
        let portsHtml = '';
        if (data.network.firewall.open_ports && data.network.firewall.open_ports.length > 0) {
            portsHtml = data.network.firewall.open_ports.slice(0, 10).map(port => 
                `<span class="status-badge status-active">${port}</span>`
            ).join(' ');
        }
        
        firewallDiv.innerHTML = `
            <div class="info-row">
                <span class="label">UFW Status</span>
                <span class="value">${data.network.firewall.ufw_status || 'N/A'}</span>
            </div>
            <div style="margin-top: 15px;">
                <div style="color: var(--text-secondary); font-size: 12px; margin-bottom: 10px;">Open Ports:</div>
                ${portsHtml || '<span style="color: var(--text-secondary); font-size: 12px;">No data</span>'}
            </div>
        `;
    }
}

// Update Services
function updateServices(data) {
    if (!data.services || !data.services.services) return;
    
    const servicesDiv = document.getElementById('services-list');
    servicesDiv.innerHTML = '';
    
    data.services.services.forEach(svc => {
        const item = document.createElement('div');
        item.className = 'service-item';
        item.innerHTML = `
            <div class="service-name">${svc.name}</div>
            <div class="service-status">
                <span class="status-badge ${svc.status === 'active' ? 'status-active' : 'status-inactive'}">${svc.status}</span>
                <span class="status-badge ${svc.enabled === 'enabled' ? 'status-active' : 'status-inactive'}">${svc.enabled}</span>
            </div>
        `;
        servicesDiv.appendChild(item);
    });
}

// Update Processes
function updateProcesses(data) {
    if (!data.processes) return;
    
    // Top CPU
    const cpuDiv = document.getElementById('processes-cpu');
    cpuDiv.innerHTML = '';
    
    if (data.processes.top_cpu) {
        data.processes.top_cpu.forEach(proc => {
            const item = document.createElement('div');
            item.className = 'process-item';
            item.innerHTML = `
                <span class="process-name">${proc.name} (${proc.pid})</span>
                <span class="process-value">${proc.cpu_percent ? proc.cpu_percent.toFixed(1) : '0.0'}%</span>
            `;
            cpuDiv.appendChild(item);
        });
    }
    
    // Top Memory
    const memDiv = document.getElementById('processes-memory');
    memDiv.innerHTML = '';
    
    if (data.processes.top_memory) {
        data.processes.top_memory.forEach(proc => {
            const item = document.createElement('div');
            item.className = 'process-item';
            item.innerHTML = `
                <span class="process-name">${proc.name} (${proc.pid})</span>
                <span class="process-value">${proc.memory_percent ? proc.memory_percent.toFixed(1) : '0.0'}%</span>
            `;
            memDiv.appendChild(item);
        });
    }
}

// Update Security
function updateSecurity(data) {
    if (!data.security) return;
    
    // Logged users
    const usersDiv = document.getElementById('security-users');
    usersDiv.innerHTML = '';
    
    if (data.security.logged_users && data.security.logged_users.length > 0) {
        data.security.logged_users.forEach(user => {
            const item = document.createElement('div');
            item.innerHTML = `
                <div class="info-row">
                    <span class="label">${user.name}@${user.terminal}</span>
                    <span class="value">${user.started}</span>
                </div>
            `;
            usersDiv.appendChild(item);
        });
    } else {
        usersDiv.innerHTML = '<div class="loading">No logged users</div>';
    }
    
    // Failed logins
    const failedDiv = document.getElementById('security-failed');
    failedDiv.innerHTML = '';
    
    if (data.security.failed_logins && data.security.failed_logins.length > 0) {
        const logContainer = document.createElement('div');
        logContainer.className = 'log-container';
        data.security.failed_logins.slice(0, 20).forEach(line => {
            if (line.trim()) {
                const logLine = document.createElement('div');
                logLine.className = 'log-line';
                logLine.textContent = line;
                logContainer.appendChild(logLine);
            }
        });
        failedDiv.appendChild(logContainer);
    } else {
        failedDiv.innerHTML = '<div class="loading">No failed login attempts</div>';
    }
}

// Update Storage
function updateStorage(data) {
    if (!data.disk || !data.disk.partitions) return;
    
    const storageDiv = document.getElementById('storage-details');
    storageDiv.innerHTML = '';
    
    data.disk.partitions.forEach(part => {
        const item = document.createElement('div');
        item.style.marginBottom = '20px';
        
        let statusColor = 'status-active';
        if (part.percent > 80) statusColor = 'status-inactive';
        else if (part.percent > 60) statusColor = 'status-warning';
        
        item.innerHTML = `
            <div class="disk-header">
                <span class="disk-path">${part.mountpoint}</span>
                <span class="status-badge ${statusColor}">${part.percent.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${part.percent}%"></div>
            </div>
            <div class="info-row">
                <span class="label">Device</span>
                <span class="value">${part.device}</span>
            </div>
            <div class="info-row">
                <span class="label">Filesystem</span>
                <span class="value">${part.fstype}</span>
            </div>
            <div class="info-row">
                <span class="label">Total</span>
                <span class="value">${formatBytes(part.total)}</span>
            </div>
            <div class="info-row">
                <span class="label">Used</span>
                <span class="value">${formatBytes(part.used)}</span>
            </div>
            <div class="info-row">
                <span class="label">Free</span>
                <span class="value">${formatBytes(part.free)}</span>
            </div>
            <div class="info-row">
                <span class="label">Read Count</span>
                <span class="value">${part.read_count}</span>
            </div>
            <div class="info-row">
                <span class="label">Write Count</span>
                <span class="value">${part.write_count}</span>
            </div>
        `;
        storageDiv.appendChild(item);
    });
}

// Update Docker
function updateDocker(data) {
    if (!data.docker) return;
    
    const containersDiv = document.getElementById('docker-containers');
    const imagesDiv = document.getElementById('docker-images');
    
    if (!data.docker.installed) {
        containersDiv.innerHTML = '<div class="loading">Docker not installed</div>';
        imagesDiv.innerHTML = '<div class="loading">Docker not installed</div>';
        return;
    }
    
    // Containers
    containersDiv.innerHTML = '';
    if (data.docker.containers && data.docker.containers.length > 0) {
        data.docker.containers.forEach(container => {
            const item = document.createElement('div');
            item.className = 'service-item';
            const isRunning = container.status.toLowerCase().includes('up');
            item.innerHTML = `
                <div>
                    <div class="service-name">${container.name}</div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">${container.image}</div>
                </div>
                <span class="status-badge ${isRunning ? 'status-active' : 'status-inactive'}">${container.status}</span>
            `;
            containersDiv.appendChild(item);
        });
    } else {
        containersDiv.innerHTML = '<div class="loading">No containers</div>';
    }
    
    // Images
    imagesDiv.innerHTML = '';
    if (data.docker.images && data.docker.images.length > 0) {
        data.docker.images.forEach(image => {
            const item = document.createElement('div');
            item.className = 'process-item';
            item.innerHTML = `
                <span class="process-name">${image.name}</span>
                <span class="process-value">${image.size}</span>
            `;
            imagesDiv.appendChild(item);
        });
    } else {
        imagesDiv.innerHTML = '<div class="loading">No images</div>';
    }
}

// Load page specific data
async function loadPageData(page) {
    try {
        const response = await fetch('/api/all');
        const data = await response.json();
        
        switch(page) {
            case 'overview':
                updateOverview(data);
                break;
            case 'server-status':
                updateServerStatus(data);
                break;
            case 'hardware':
                updateHardware(data);
                break;
            case 'network':
                updateNetwork(data);
                break;
            case 'services':
                updateServices(data);
                break;
            case 'processes':
                updateProcesses(data);
                break;
            case 'security':
                updateSecurity(data);
                break;
            case 'storage':
                updateStorage(data);
                break;
            case 'docker':
                updateDocker(data);
                break;
            case 'logs':
                loadLogs();
                break;
        }
    } catch (error) {
        console.error('Error loading page data:', error);
    }
}

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        // Syslog
        const syslogDiv = document.getElementById('logs-syslog');
        syslogDiv.innerHTML = '';
        if (data.syslog && data.syslog.length > 0) {
            data.syslog.forEach(line => {
                if (line.trim()) {
                    const logLine = document.createElement('div');
                    logLine.className = 'log-line';
                    logLine.textContent = line;
                    syslogDiv.appendChild(logLine);
                }
            });
        } else {
            syslogDiv.innerHTML = '<div class="loading">No logs available</div>';
        }
        
        // Auth log
        const authDiv = document.getElementById('logs-auth');
        authDiv.innerHTML = '';
        if (data.auth && data.auth.length > 0) {
            data.auth.forEach(line => {
                if (line.trim()) {
                    const logLine = document.createElement('div');
                    logLine.className = 'log-line';
                    logLine.textContent = line;
                    authDiv.appendChild(logLine);
                }
            });
        } else {
            authDiv.innerHTML = '<div class="loading">No logs available</div>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Protect author info
    protectAuthorInfo();
    
    // Initialize charts
    initCharts();
    
    // Load initial data
    loadAllData();
    
    // Update server time
    updateServerTime();
    setInterval(updateServerTime, 1000);
    
    // Auto refresh data every 1 second
    setInterval(loadAllData, 1000);
});

// Protect author information from being modified
function protectAuthorInfo() {
    // Disable right-click on author sections
    const authorSections = document.querySelectorAll('.author-info, .donation-box, .author-badge');
    authorSections.forEach(section => {
        section.addEventListener('contextmenu', (e) => e.preventDefault());
        section.style.userSelect = 'none';
        section.style.pointerEvents = 'auto';
    });
    
    // Prevent text selection on author info
    document.querySelector('.author-name').style.userSelect = 'none';
    document.querySelector('.author-badge').style.userSelect = 'none';
    
    // Monitor DOM changes to prevent modification
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                const authorName = document.querySelector('.author-name');
                const authorBadge = document.querySelector('.author-badge');
                const donationTitle = document.querySelector('.donation-title');
                
                if (authorName && !authorName.textContent.includes('M. Nafiurohman')) {
                    authorName.textContent = 'M. Nafiurohman';
                }
                if (authorBadge && !authorBadge.textContent.includes('M. Nafiurohman')) {
                    authorBadge.textContent = 'by M. Nafiurohman';
                }
                if (donationTitle && !donationTitle.textContent.includes('Belikan Developer Kopi')) {
                    donationTitle.innerHTML = '<i class="fas fa-coffee"></i> Belikan Developer Kopi';
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
    
    // Prevent console tampering
    const originalLog = console.log;
    console.log = function(...args) {
        if (args.some(arg => typeof arg === 'string' && arg.includes('author'))) {
            return;
        }
        originalLog.apply(console, args);
    };
}
