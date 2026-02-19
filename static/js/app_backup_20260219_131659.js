// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');
        
        // Get page name
        const page = item.dataset.page;
        
        // Update title
        const title = item.querySelector('span').textContent;
        document.getElementById('currentPageTitle').textContent = title;
        
        // Lazy load page
        console.log(`🔄 Loading page: ${page}`);
        loadPage(page);
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
                updateCPUCoreChart();
                updateGPUChart();
                break;
            case 'server-status':
                updateServerStatus(data);
                break;
            case 'hardware':
                updateHardware(data);
                updateCPUCoreChart();
                updateGPUChart();
                break;
            case 'network':
                updateNetwork(data);
                loadNetworkTraffic();
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
                loadStorageBrowser();
                break;
            case 'docker':
                updateDocker(data);
                break;
            case 'kubernetes':
                loadKubernetes();
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
    console.log('🚀 Initializing dashboard...');
    
    // Protect author info
    protectAuthorInfo();
    
    // Load initial page (overview) - MUST BE FIRST
    if (typeof loadPage === 'function') {
        console.log('📄 Loading overview page...');
        loadPage('overview');
        
        // Initialize charts after page load
        setTimeout(() => {
            console.log('📊 Initializing charts...');
            initCharts();
            initCPUCoreChart();
            initGPUChart();
        }, 300);
    } else {
        console.error('❌ loadPage function not found!');
    }
    
    // Load initial data
    setTimeout(() => {
        console.log('📡 Loading initial data...');
        loadAllData();
    }, 500);
    
    // Update server time
    updateServerTime();
    setInterval(updateServerTime, 1000);
    
    // ANTI-PANAS: 3 detik interval + tab visibility detection
    function startRefresh() {
        // Main data refresh every 3 seconds
        setInterval(() => {
            if (!document.hidden) {
                loadAllData();
            }
        }, 3000);
        
        // Charts refresh every 5 seconds
        setInterval(() => {
            if (!document.hidden) {
                updateCPUCoreChart();
                updateGPUChart();
            }
        }, 5000);
        
        // Network traffic refresh every 5 seconds
        setInterval(() => {
            if (!document.hidden && window.currentPage === 'network') {
                loadNetworkTraffic();
            }
        }, 5000);
        
        // Kubernetes refresh every 10 seconds
        setInterval(() => {
            if (!document.hidden && window.currentPage === 'kubernetes') {
                loadKubernetes();
            }
        }, 10000);
    }
    
    // Start refresh
    startRefresh();
    
    // Pause refresh when tab is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('⏸️ Tab hidden - refresh paused');
        } else {
            console.log('▶️ Tab visible - refresh resumed');
            loadAllData();
        }
    });
    
    console.log('✅ Dashboard initialized successfully');
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

// Storage Browser
async function loadStorageBrowser() {
    try {
        const response = await fetch('/api/storage/summary');
        const data = await response.json();
        
        const browserDiv = document.getElementById('storage-browser');
        if (!browserDiv) return;
        
        browserDiv.innerHTML = '';
        
        data.forEach(partition => {
            const item = document.createElement('div');
            item.className = 'storage-partition';
            item.innerHTML = `
                <div class="partition-header" onclick="togglePartition('${partition.mountpoint}')">
                    <i class="fas fa-folder"></i>
                    <span>${partition.mountpoint}</span>
                    <span class="partition-size">${partition.used_human} / ${partition.total_human}</span>
                </div>
                <div id="partition-${partition.mountpoint.replace(/\//g, '-')}" class="partition-content" style="display: none;">
                    <div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading...</div>
                </div>
            `;
            browserDiv.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading storage browser:', error);
    }
}

async function togglePartition(mountpoint) {
    const contentId = `partition-${mountpoint.replace(/\//g, '-')}`;
    const contentDiv = document.getElementById(contentId);
    
    if (contentDiv.style.display === 'none') {
        contentDiv.style.display = 'block';
        
        // Load large files
        try {
            const response = await fetch(`/api/storage/large-files?path=${encodeURIComponent(mountpoint)}&min_size=100`);
            const files = await response.json();
            
            contentDiv.innerHTML = '';
            
            if (files.length > 0) {
                files.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <i class="fas fa-file"></i>
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${file.size_human}</span>
                    `;
                    contentDiv.appendChild(fileItem);
                });
            } else {
                contentDiv.innerHTML = '<div class="loading">No large files (>100MB) found</div>';
            }
        } catch (error) {
            contentDiv.innerHTML = '<div class="loading">Error loading files</div>';
        }
    } else {
        contentDiv.style.display = 'none';
    }
}

// Network Traffic Details
let networkTrafficChart;

async function loadNetworkTraffic() {
    try {
        const response = await fetch('/api/network/traffic');
        const interfaces = await response.json();
        
        const trafficDiv = document.getElementById('network-traffic-details');
        if (!trafficDiv) return;
        
        trafficDiv.innerHTML = '';
        
        interfaces.forEach(iface => {
            if (iface.name === 'lo') return; // Skip loopback
            
            const item = document.createElement('div');
            item.className = 'traffic-interface';
            item.innerHTML = `
                <div class="interface-header">
                    <span class="interface-name">${iface.name}</span>
                    <span class="status-badge ${iface.status === 'up' ? 'status-active' : 'status-inactive'}">${iface.status}</span>
                </div>
                <div class="traffic-stats">
                    <div class="stat-item">
                        <i class="fas fa-arrow-up text-warning"></i>
                        <span class="stat-label">Upload</span>
                        <span class="stat-value">${iface.upload_rate_human}</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-arrow-down text-info"></i>
                        <span class="stat-label">Download</span>
                        <span class="stat-value">${iface.download_rate_human}</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-exchange-alt"></i>
                        <span class="stat-label">Total Sent</span>
                        <span class="stat-value">${iface.bytes_sent_human}</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-exchange-alt"></i>
                        <span class="stat-label">Total Recv</span>
                        <span class="stat-value">${iface.bytes_recv_human}</span>
                    </div>
                </div>
                <div class="info-row">
                    <span class="label">Packets Sent/Recv</span>
                    <span class="value">${iface.packets_sent_rate}/s | ${iface.packets_recv_rate}/s</span>
                </div>
                <div class="info-row">
                    <span class="label">Errors (In/Out)</span>
                    <span class="value">${iface.errors_in} / ${iface.errors_out}</span>
                </div>
                <div class="info-row">
                    <span class="label">Drops (In/Out)</span>
                    <span class="value">${iface.drops_in} / ${iface.drops_out}</span>
                </div>
            `;
            trafficDiv.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading network traffic:', error);
    }
}

// Kubernetes Monitoring
async function loadKubernetes() {
    try {
        // Check if K8s is available
        const availResponse = await fetch('/api/k8s/available');
        const availData = await availResponse.json();
        
        if (!availData.available) {
            document.getElementById('k8s-pods').innerHTML = '<div class="loading">Kubernetes not available</div>';
            document.getElementById('k8s-services').innerHTML = '<div class="loading">Kubernetes not available</div>';
            document.getElementById('k8s-deployments').innerHTML = '<div class="loading">Kubernetes not available</div>';
            return;
        }
        
        // Load pods
        const podsResponse = await fetch('/api/k8s/pods');
        const pods = await podsResponse.json();
        
        const podsDiv = document.getElementById('k8s-pods');
        podsDiv.innerHTML = '';
        
        if (pods.length > 0) {
            pods.forEach(pod => {
                const item = document.createElement('div');
                item.className = 'k8s-item';
                const statusClass = pod.status === 'Running' ? 'status-active' : 'status-inactive';
                item.innerHTML = `
                    <div class="k8s-name">${pod.name}</div>
                    <div class="k8s-details">
                        <span class="status-badge ${statusClass}">${pod.status}</span>
                        <span class="k8s-namespace">${pod.namespace}</span>
                        <span class="k8s-restarts">Restarts: ${pod.restarts}</span>
                    </div>
                `;
                podsDiv.appendChild(item);
            });
        } else {
            podsDiv.innerHTML = '<div class="loading">No pods found</div>';
        }
        
        // Load services
        const servicesResponse = await fetch('/api/k8s/services');
        const services = await servicesResponse.json();
        
        const servicesDiv = document.getElementById('k8s-services');
        servicesDiv.innerHTML = '';
        
        if (services.length > 0) {
            services.forEach(svc => {
                const item = document.createElement('div');
                item.className = 'k8s-item';
                item.innerHTML = `
                    <div class="k8s-name">${svc.name}</div>
                    <div class="k8s-details">
                        <span class="status-badge status-active">${svc.type}</span>
                        <span class="k8s-namespace">${svc.namespace}</span>
                        <span class="k8s-ports">${svc.ports}</span>
                    </div>
                `;
                servicesDiv.appendChild(item);
            });
        } else {
            servicesDiv.innerHTML = '<div class="loading">No services found</div>';
        }
        
        // Load deployments
        const deploymentsResponse = await fetch('/api/k8s/deployments');
        const deployments = await deploymentsResponse.json();
        
        const deploymentsDiv = document.getElementById('k8s-deployments');
        deploymentsDiv.innerHTML = '';
        
        if (deployments.length > 0) {
            deployments.forEach(dep => {
                const item = document.createElement('div');
                item.className = 'k8s-item';
                const statusClass = dep.ready === dep.replicas ? 'status-active' : 'status-warning';
                item.innerHTML = `
                    <div class="k8s-name">${dep.name}</div>
                    <div class="k8s-details">
                        <span class="status-badge ${statusClass}">${dep.ready}/${dep.replicas}</span>
                        <span class="k8s-namespace">${dep.namespace}</span>
                    </div>
                `;
                deploymentsDiv.appendChild(item);
            });
        } else {
            deploymentsDiv.innerHTML = '<div class="loading">No deployments found</div>';
        }
    } catch (error) {
        console.error('Error loading Kubernetes:', error);
    }
}

// GPU Monitoring Chart
let gpuChart;

function initGPUChart() {
    const gpuCtx = document.getElementById('gpuChart');
    if (!gpuCtx) return;
    
    gpuChart = new Chart(gpuCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'GPU Utilization %',
                data: [],
                backgroundColor: 'rgba(139, 92, 246, 0.6)',
                borderColor: '#8b5cf6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 31, 58, 0.9)',
                    titleColor: '#e8f0ff',
                    bodyColor: '#a8c5e8'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(46, 90, 143, 0.2)' },
                    ticks: { color: '#a8c5e8' }
                },
                x: {
                    grid: { color: 'rgba(46, 90, 143, 0.2)' },
                    ticks: { color: '#a8c5e8' }
                }
            }
        }
    });
}

async function updateGPUChart() {
    try {
        const response = await fetch('/api/gpu');
        const data = await response.json();
        
        if (!gpuChart || !data.gpus || data.gpus.length === 0) return;
        
        const labels = data.gpus.map((gpu, i) => `GPU ${i}`);
        const utilization = data.gpus.map(gpu => gpu.utilization || 0);
        
        gpuChart.data.labels = labels;
        gpuChart.data.datasets[0].data = utilization;
        gpuChart.update('none');
    } catch (error) {
        console.error('Error updating GPU chart:', error);
    }
}

// CPU Per-Core Chart
let cpuCoreChart;

function initCPUCoreChart() {
    const coreCtx = document.getElementById('cpuCoreChart');
    if (!coreCtx) return;
    
    cpuCoreChart = new Chart(coreCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Core Usage %',
                data: [],
                backgroundColor: 'rgba(74, 143, 216, 0.6)',
                borderColor: '#4a8fd8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 31, 58, 0.9)',
                    titleColor: '#e8f0ff',
                    bodyColor: '#a8c5e8'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(46, 90, 143, 0.2)' },
                    ticks: { color: '#a8c5e8' }
                },
                x: {
                    grid: { color: 'rgba(46, 90, 143, 0.2)' },
                    ticks: { color: '#a8c5e8', font: { size: 9 } }
                }
            }
        }
    });
}

async function updateCPUCoreChart() {
    try {
        const response = await fetch('/api/cpu');
        const data = await response.json();
        
        if (!cpuCoreChart || !data.per_core_usage) return;
        
        const labels = data.per_core_usage.map((_, i) => `C${i}`);
        const usage = data.per_core_usage;
        
        cpuCoreChart.data.labels = labels;
        cpuCoreChart.data.datasets[0].data = usage;
        cpuCoreChart.update('none');
    } catch (error) {
        console.error('Error updating CPU core chart:', error);
    }
}
