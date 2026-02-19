#!/usr/bin/env python3
"""
Generate HTML documentation from markdown files
"""

import os
import markdown
from pathlib import Path

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - System Monitor</title>
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
        h1 {{ color: #4a8fd8; margin-bottom: 20px; }}
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
        pre code {{
            background: none;
            padding: 0;
        }}
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
            color: #a8c5e8;
        }}
        li {{ margin-bottom: 8px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid rgba(46, 90, 143, 0.3);
        }}
        th {{
            background: rgba(46, 90, 143, 0.3);
            color: #4a8fd8;
            font-weight: 600;
        }}
        td {{ color: #a8c5e8; }}
        a {{ color: #4a8fd8; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #a8c5e8;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid rgba(46, 90, 143, 0.3);
        }}
        .version {{
            display: inline-block;
            background: rgba(46, 90, 143, 0.3);
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Back to Documentation</a>
        <div class="content">
{content}
        </div>
        <div class="footer">
            <p>Made with ❤️ by M. Nafiurohman <span class="version">mntr26.02.19/14.30</span></p>
        </div>
    </div>
</body>
</html>
"""

def convert_md_to_html(md_file, output_file, title):
    """Convert markdown file to HTML"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
        
        # Generate full HTML
        full_html = HTML_TEMPLATE.format(title=title, content=html_content)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ Generated: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error converting {md_file}: {e}")
        return False

def main():
    # Get script directory
    script_dir = Path(__file__).parent
    docs_dir = script_dir / 'docs'
    
    # Create docs directory if not exists
    docs_dir.mkdir(exist_ok=True)
    
    # Markdown files to convert
    conversions = [
        ('QUICKSTART_GUIDE.md', 'quickstart.html', 'Quick Start Guide'),
        ('COMPLETE_IMPLEMENTATION.md', 'features.html', 'Features Overview'),
        ('README.md', 'installation.html', 'Installation Guide'),
        ('API.md', 'api.html', 'API Reference'),
        ('TROUBLESHOOTING.md', 'troubleshooting.html', 'Troubleshooting'),
        ('PERFORMANCE.md', 'performance.html', 'Performance Guide'),
        ('PROTECTION.md', 'security.html', 'Security Guide'),
        ('CHANGELOG.md', 'changelog.html', 'Changelog'),
    ]
    
    print("=" * 60)
    print("Generating HTML Documentation")
    print("=" * 60)
    print()
    
    success_count = 0
    for md_file, html_file, title in conversions:
        md_path = script_dir / md_file
        html_path = docs_dir / html_file
        
        if md_path.exists():
            if convert_md_to_html(md_path, html_path, title):
                success_count += 1
        else:
            print(f"⚠️  Skipped: {md_file} (not found)")
    
    print()
    print("=" * 60)
    print(f"Generated {success_count}/{len(conversions)} documentation files")
    print(f"Documentation available at: {docs_dir}/index.html")
    print("=" * 60)

if __name__ == '__main__':
    main()
