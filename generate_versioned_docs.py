#!/usr/bin/env python3
"""
Generate Versioned HTML Documentation
Each doc type gets its own versioned file
"""

import os
from datetime import datetime
from pathlib import Path

VERSION = datetime.now().strftime("mntr%y.%m.%d-%H.%M")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a1628 0%, #0f1f3a 100%);
            color: #e8f0ff;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(15, 31, 58, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(46, 90, 143, 0.3);
            border-radius: 12px;
            padding: 40px;
        }}
        .back-link {{
            display: inline-block;
            color: #4a8fd8;
            text-decoration: none;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .back-link:hover {{ text-decoration: underline; }}
        h1 {{ color: #4a8fd8; margin-bottom: 10px; }}
        h2 {{ color: #4a8fd8; margin-top: 30px; margin-bottom: 15px; }}
        h3 {{ color: #6aa8e8; margin-top: 20px; margin-bottom: 10px; }}
        h4 {{ color: #8ab8f0; margin-top: 15px; margin-bottom: 8px; }}
        p {{ margin-bottom: 15px; color: #a8c5e8; }}
        code {{
            background: rgba(10, 22, 40, 0.5);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e8f0ff;
        }}
        pre {{
            background: rgba(10, 22, 40, 0.5);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 20px;
        }}
        pre code {{ background: none; padding: 0; }}
        ul, ol {{ margin-left: 30px; margin-bottom: 15px; color: #a8c5e8; }}
        li {{ margin-bottom: 8px; }}
        .version {{
            display: inline-block;
            background: rgba(46, 90, 143, 0.3);
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #a8c5e8;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid rgba(46, 90, 143, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Back to Documentation</a>
        <h1>{title}</h1>
        <div class="version">{version}</div>
        <div class="content">
{content}
        </div>
        <div class="footer">
            <p>Made with ❤️ by M. Nafiurohman</p>
        </div>
    </div>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitor Documentation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a1628 0%, #0f1f3a 100%);
            color: #e8f0ff;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(15, 31, 58, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(46, 90, 143, 0.3);
            border-radius: 12px;
            padding: 40px;
        }}
        h1 {{ color: #4a8fd8; margin-bottom: 10px; font-size: 36px; }}
        .version {{ color: #a8c5e8; font-size: 14px; margin-bottom: 30px; }}
        .doc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .doc-card {{
            background: rgba(46, 90, 143, 0.2);
            border: 1px solid rgba(46, 90, 143, 0.3);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s;
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .doc-card:hover {{
            background: rgba(46, 90, 143, 0.3);
            transform: translateY(-2px);
        }}
        .doc-card h3 {{ color: #4a8fd8; margin-bottom: 10px; font-size: 20px; }}
        .doc-card p {{ color: #a8c5e8; font-size: 14px; }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #a8c5e8;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid rgba(46, 90, 143, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 System Monitor Documentation</h1>
        <div class="version">{version}</div>
        <p style="margin-bottom: 30px;">Complete documentation for System Monitor Dashboard</p>
        <div class="doc-grid">
            <a href="quickstart-{version}.html" class="doc-card">
                <h3>🚀 Quick Start</h3>
                <p>Get started quickly</p>
            </a>
            <a href="features-{version}.html" class="doc-card">
                <h3>✨ Features</h3>
                <p>All monitoring features</p>
            </a>
            <a href="installation-{version}.html" class="doc-card">
                <h3>📦 Installation</h3>
                <p>Installation guide</p>
            </a>
            <a href="configuration-{version}.html" class="doc-card">
                <h3>⚙️ Configuration</h3>
                <p>Configure settings</p>
            </a>
            <a href="api-{version}.html" class="doc-card">
                <h3>🔌 API Reference</h3>
                <p>API endpoints</p>
            </a>
            <a href="troubleshooting-{version}.html" class="doc-card">
                <h3>🔧 Troubleshooting</h3>
                <p>Common issues</p>
            </a>
            <a href="performance-{version}.html" class="doc-card">
                <h3>⚡ Performance</h3>
                <p>Optimization tips</p>
            </a>
            <a href="security-{version}.html" class="doc-card">
                <h3>🔒 Security</h3>
                <p>Security guide</p>
            </a>
            <a href="changelog-{version}.html" class="doc-card">
                <h3>📝 Changelog</h3>
                <p>Version history</p>
            </a>
        </div>
        <div class="footer">
            <p>Made with ❤️ by M. Nafiurohman</p>
        </div>
    </div>
</body>
</html>
"""

def create_doc(title, content, filename):
    """Create versioned HTML doc"""
    html = HTML_TEMPLATE.format(
        title=title,
        version=VERSION,
        content=content
    )
    filepath = Path('docs') / f"{VERSION}-{filename}.html"
    filepath.write_text(html, encoding='utf-8')
    print(f"✅ {filepath}")

def main():
    Path('docs').mkdir(exist_ok=True)
    
    print("=" * 60)
    print(f"Generating Documentation - Version: {VERSION}")
    print("=" * 60)
    
    # Index
    index_html = INDEX_TEMPLATE.format(version=VERSION)
    index_path = Path('docs') / f"{VERSION}-index.html"
    index_path.write_text(index_html, encoding='utf-8')
    print(f"✅ {index_path}")
    
    # Quick Start
    create_doc("🚀 Quick Start Guide", """
<h2>Installation</h2>
<pre><code>git clone https://github.com/nafiurohman/system-monitoring.git
cd system-monitoring
pip3 install -r requirements.txt
python3 app.py</code></pre>

<h2>Access Dashboard</h2>
<p>Open browser: <code>http://127.0.0.1:9999</code></p>

<h2>Features</h2>
<ul>
<li>CPU per-thread monitoring</li>
<li>GPU cards + charts</li>
<li>Network status (4 indicators)</li>
<li>Process Manager (Task Manager style)</li>
<li>Security monitoring</li>
<li>Storage browser</li>
</ul>
""", "quickstart")
    
    # Features
    create_doc("✨ Features Overview", """
<h2>Core Monitoring</h2>
<ul>
<li><strong>CPU</strong>: Per-thread usage, temperature, load average</li>
<li><strong>GPU</strong>: Multi-vendor (NVIDIA/AMD/Intel), utilization, temperature</li>
<li><strong>Memory</strong>: Detailed breakdown (used, free, cached, buffers, active, inactive)</li>
<li><strong>Network</strong>: Traffic details, status indicators, internet check</li>
<li><strong>Disk</strong>: Partitions, SMART status, I/O stats</li>
</ul>

<h2>Advanced Features</h2>
<ul>
<li><strong>Performance Metrics</strong>: Context switches, interrupts, file descriptors</li>
<li><strong>Thermal & Power</strong>: CPU temp, battery, throttling</li>
<li><strong>Security</strong>: Score, firewall, antivirus, ports analysis</li>
<li><strong>Process Manager</strong>: Sortable, searchable, color-coded</li>
<li><strong>Storage Browser</strong>: Dropdown, large files detection</li>
</ul>
""", "features")
    
    # Installation
    create_doc("📦 Installation Guide", """
<h2>Requirements</h2>
<ul>
<li>Python 3.8+</li>
<li>pip3</li>
<li>Linux/Windows/macOS</li>
</ul>

<h2>Quick Install</h2>
<pre><code>git clone https://github.com/nafiurohman/system-monitoring.git
cd system-monitoring
chmod +x install.sh
./install.sh</code></pre>

<h2>Manual Install</h2>
<pre><code>pip3 install -r requirements.txt
python3 app.py</code></pre>
""", "installation")
    
    # Configuration
    create_doc("⚙️ Configuration", """
<h2>Change Port</h2>
<pre><code>app.run(host='127.0.0.1', port=9999, debug=False)</code></pre>

<h2>Change Refresh Interval</h2>
<pre><code>setInterval(() => {
    if (!document.hidden) {
        loadAllData();
    }
}, 3000); // 3 seconds</code></pre>

<h2>Cache TTL</h2>
<pre><code>CACHE_TTL = 0.5  # seconds</code></pre>
""", "configuration")
    
    # API
    create_doc("🔌 API Reference", """
<h2>Endpoints</h2>
<ul>
<li><code>GET /api/version</code> - Version info</li>
<li><code>GET /api/cpu</code> - CPU with per-thread</li>
<li><code>GET /api/gpu</code> - GPU info</li>
<li><code>GET /api/memory</code> - Memory details</li>
<li><code>GET /api/performance</code> - Performance metrics</li>
<li><code>GET /api/thermal</code> - Thermal & power</li>
<li><code>GET /api/internet</code> - Internet check</li>
<li><code>GET /api/security</code> - Security info</li>
<li><code>GET /api/process-list</code> - Process list</li>
<li><code>GET /api/network</code> - Network info</li>
<li><code>GET /api/all</code> - All data</li>
</ul>
""", "api")
    
    # Troubleshooting
    create_doc("🔧 Troubleshooting", """
<h2>Process List Error</h2>
<p><strong>Fixed</strong>: KeyError resolved with .get() method</p>

<h2>Port Already in Use</h2>
<pre><code>sudo lsof -ti:9999 | xargs kill -9</code></pre>

<h2>GPU Not Detected</h2>
<p>Install drivers: nvidia-smi, rocm-smi, or Intel drivers</p>

<h2>Services Not Showing</h2>
<p>Windows: Run as Administrator<br>Linux: Check systemctl permissions</p>
""", "troubleshooting")
    
    # Performance
    create_doc("⚡ Performance Guide", """
<h2>Optimization Tips</h2>
<ul>
<li>Reduce refresh interval (3s → 5s)</li>
<li>Limit processes (100 → 50)</li>
<li>Disable unused charts</li>
<li>Close unused tabs</li>
<li>Keep cache TTL at 0.5s</li>
</ul>

<h2>Performance Metrics</h2>
<ul>
<li>Context switches</li>
<li>Interrupts</li>
<li>File descriptors</li>
<li>Thread count</li>
<li>Zombie processes</li>
</ul>
""", "performance")
    
    # Security
    create_doc("🔒 Security Guide", """
<h2>Best Practices</h2>
<ul>
<li>Bind to localhost (127.0.0.1)</li>
<li>Use SSH tunnel for remote access</li>
<li>Add authentication (Flask-HTTPAuth)</li>
<li>Use HTTPS with reverse proxy</li>
<li>Configure firewall rules</li>
</ul>

<h2>Security Features</h2>
<ul>
<li>Security score (0-100)</li>
<li>Firewall detection</li>
<li>Antivirus status</li>
<li>Open ports analysis</li>
<li>Risk assessment</li>
</ul>
""", "security")
    
    # Changelog
    create_doc("📝 Changelog", """
<h2>Version {}</h2>
<ul>
<li>✅ CPU per-thread monitoring (all threads)</li>
<li>✅ GPU cards + dual chart</li>
<li>✅ Network status (4 indicators)</li>
<li>✅ Performance deep metrics</li>
<li>✅ Thermal & power monitoring</li>
<li>✅ Process Manager with refresh</li>
<li>✅ Storage browser with dropdown</li>
<li>✅ Security monitoring enhanced</li>
<li>✅ HTML documentation (versioned)</li>
<li>✅ Full-screen optimized</li>
</ul>
""".format(VERSION), "changelog")
    
    print("=" * 60)
    print(f"✅ Generated 9 versioned documentation files")
    print(f"📁 Location: docs/")
    print(f"🌐 Open: docs/index-{VERSION}.html")
    print("=" * 60)

if __name__ == '__main__':
    main()
