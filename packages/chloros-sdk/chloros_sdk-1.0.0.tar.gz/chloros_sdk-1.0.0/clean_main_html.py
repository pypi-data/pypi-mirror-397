#!/usr/bin/env python3
"""
Clean debug console logs from main.html
"""

import re
from pathlib import Path

def clean_html(filepath):
    """Remove debug console statements from HTML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Tags to remove
        debug_patterns = [
            r'\[DEBUG\]',
            r'\[ELECTRON PROGRESS\]',
            r'🚀', r'🔧', r'🔍', r'🎨', r'🔌', r'📦', r'✅', r'🔄', r'🖼️',
        ]
        
        pattern = '|'.join(debug_patterns)
        
        # Remove console.log/debug/info/warn lines with debug patterns
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Check if line has console statement with debug pattern
            if re.search(r'console\.(log|debug|info|warn)', line):
                if re.search(pattern, line):
                    # Skip this line (remove it)
                    continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        removed = len(lines) - len(cleaned_lines)
        
        if content != original:
            # Backup
            backup_path = str(filepath) + '.final_backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Removed {removed} debug console lines from {filepath.name}")
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {e}')
        return False, 0

def main():
    html_file = Path('ui/main.html')
    
    if html_file.exists():
        clean_html(html_file)
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == '__main__':
    main()

