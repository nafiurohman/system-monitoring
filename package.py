#!/usr/bin/env python3
"""
Package System Monitor as Application
Supports: .deb (Linux), .tar.xz (Linux), .exe (Windows)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

VERSION = "26.02.19-14.38"
APP_NAME = "system-monitor"
AUTHOR = "M. Nafiurohman"
EMAIL = "nafiurohman25@gmail.com"

def create_deb_package():
    """Create .deb package for Debian/Ubuntu"""
    print("📦 Creating .deb package...")
    
    # Create directory structure
    deb_dir = Path(f"{APP_NAME}_{VERSION}")
    deb_dir.mkdir(exist_ok=True)
    
    # DEBIAN control directory
    debian_dir = deb_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)
    
    # Control file
    control = f"""Package: {APP_NAME}
Version: {VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), python3-pip, python3-flask, python3-psutil
Maintainer: {AUTHOR} <{EMAIL}>
Description: Professional server monitoring platform
 System Monitor Dashboard - Real-time server monitoring
 with CPU, GPU, Memory, Network, Security monitoring.
"""
    (debian_dir / "control").write_text(control)
    
    # Post-install script
    postinst = """#!/bin/bash
set -e

# Install Python dependencies
pip3 install flask psutil markdown --break-system-packages 2>/dev/null || pip3 install flask psutil markdown

# Create symlink
ln -sf /opt/system-monitor/monitor /usr/local/bin/monitor

echo "System Monitor installed successfully!"
echo "Run: monitor"
"""
    postinst_file = debian_dir / "postinst"
    postinst_file.write_text(postinst)
    postinst_file.chmod(0o755)
    
    # Pre-remove script
    prerm = """#!/bin/bash
set -e
rm -f /usr/local/bin/monitor
"""
    prerm_file = debian_dir / "prerm"
    prerm_file.write_text(prerm)
    prerm_file.chmod(0o755)
    
    # Application directory
    opt_dir = deb_dir / "opt" / APP_NAME
    opt_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    files_to_copy = [
        "app.py", "requirements.txt", "generate_versioned_docs.py",
        "modules", "utils", "templates", "static", "docs"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, opt_dir / item, dirs_exist_ok=True)
            else:
                shutil.copy2(src, opt_dir / item)
    
    # Create launcher script
    launcher = f"""#!/bin/bash
cd /opt/{APP_NAME}
python3 app.py
"""
    monitor_script = opt_dir / "monitor"
    monitor_script.write_text(launcher)
    monitor_script.chmod(0o755)
    
    # Build .deb
    subprocess.run(["dpkg-deb", "--build", str(deb_dir)], check=True)
    
    print(f"✅ Created: {deb_dir}.deb")
    return f"{deb_dir}.deb"

def create_tarxz_package():
    """Create .tar.xz package for Linux"""
    print("📦 Creating .tar.xz package...")
    
    pkg_dir = Path(f"{APP_NAME}-{VERSION}")
    pkg_dir.mkdir(exist_ok=True)
    
    # Copy application files
    files_to_copy = [
        "app.py", "requirements.txt", "generate_versioned_docs.py",
        "modules", "utils", "templates", "static", "docs",
        "README.md", "LICENSE"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, pkg_dir / item, dirs_exist_ok=True)
            else:
                shutil.copy2(src, pkg_dir / item)
    
    # Create install script
    install_sh = """#!/bin/bash
echo "Installing System Monitor..."

# Install dependencies
pip3 install -r requirements.txt

# Create launcher
cat > monitor << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
EOF
chmod +x monitor

echo "Installation complete!"
echo "Run: ./monitor"
"""
    (pkg_dir / "install.sh").write_text(install_sh)
    (pkg_dir / "install.sh").chmod(0o755)
    
    # Create archive
    archive_name = f"{APP_NAME}-{VERSION}.tar.xz"
    subprocess.run([
        "tar", "-cJf", archive_name, str(pkg_dir)
    ], check=True)
    
    # Cleanup
    shutil.rmtree(pkg_dir)
    
    print(f"✅ Created: {archive_name}")
    return archive_name

def create_exe_package():
    """Create .exe package for Windows using PyInstaller"""
    print("📦 Creating .exe package...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create spec file
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('docs', 'docs'),
        ('modules', 'modules'),
        ('utils', 'utils'),
    ],
    hiddenimports=['flask', 'psutil', 'markdown'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SystemMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    Path("SystemMonitor.spec").write_text(spec_content)
    
    # Build executable
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--onefile",
        "SystemMonitor.spec"
    ], check=True)
    
    exe_file = Path("dist") / "SystemMonitor.exe"
    if exe_file.exists():
        # Rename with version
        new_name = f"SystemMonitor-{VERSION}.exe"
        shutil.move(str(exe_file), new_name)
        print(f"✅ Created: {new_name}")
        return new_name
    else:
        print("❌ Failed to create .exe")
        return None

def main():
    print("=" * 60)
    print("System Monitor - Application Packager")
    print(f"Version: {VERSION}")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python3 package.py [deb|tar|exe|all]")
        print()
        print("Options:")
        print("  deb  - Create .deb package (Debian/Ubuntu)")
        print("  tar  - Create .tar.xz package (Linux)")
        print("  exe  - Create .exe package (Windows)")
        print("  all  - Create all packages")
        sys.exit(1)
    
    package_type = sys.argv[1].lower()
    
    created_packages = []
    
    try:
        if package_type in ["deb", "all"]:
            pkg = create_deb_package()
            created_packages.append(pkg)
        
        if package_type in ["tar", "all"]:
            pkg = create_tarxz_package()
            created_packages.append(pkg)
        
        if package_type in ["exe", "all"]:
            pkg = create_exe_package()
            if pkg:
                created_packages.append(pkg)
        
        print()
        print("=" * 60)
        print("✅ Packaging Complete!")
        print("=" * 60)
        print()
        print("Created packages:")
        for pkg in created_packages:
            print(f"  📦 {pkg}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
