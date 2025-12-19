#!/usr/bin/env python3
"""
Comment out console statements that contain debug tags.
Safe approach - only handles complete statements on single lines.
"""

import re
from pathlib import Path

def comment_tagged_logs(filepath):
    """Comment out console.log lines that contain debug tags"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_lines = lines[:]
        
        # Debug tags and emojis to look for
        debug_patterns = [
            r'\[DEBUG\]',
            r'\[ELECTRON PROGRESS\]',
            r'\[FILE-BROWSER\]',
            r'\[PROGRESS BAR\]',
            r'\[Progress Bar\]',
            r'\[ProgressBar',
            r'\[TAB-RENDER\]',
            r'\[SETTINGS\]',
            r'\[TIMEZONE\]',
            r'\[UPDATE-CHECKER\]',
            r'\[PROCESS BUTTON\]',
            r'\[SANDBOX\]',
            r'DEBUG\] ProgressBar',
            r'🔧', r'🔍', r'🚀', r'🎨', r'🔌', r'📦', r'✅', r'🔄', r'🖼️', r'⏳',
        ]
        
        pattern = '|'.join(debug_patterns)
        modified_count = 0
        
        for i, line in enumerate(lines):
            # If line contains console.(log|debug|info|warn) AND a debug pattern
            if re.search(r'console\.(log|debug|info|warn)', line):
                if re.search(pattern, line):
                    # Don't double-comment
                    if not line.strip().startswith('//'):
                        # Comment it out
                        indent = len(line) - len(line.lstrip())
                        lines[i] = ' ' * indent + '// ' + line.lstrip()
                        modified_count += 1
        
        if modified_count > 0:
            # Backup
            backup_path = str(filepath) + '.comment_backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(original_lines)
            
            # Write
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True, modified_count
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Comment Out Tagged Debug Logs")
    print("=" * 70)
    print()
    
    total_files = 0
    total_commented = 0
    
    # TypeScript files
    print("Processing TypeScript...")
    ts_dir = Path('ui/ts')
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            modified, count = comment_tagged_logs(ts_file)
            if modified:
                total_files += 1
                total_commented += count
                print(f'  ✓ {ts_file.name}: {count} lines commented')
    
    # HTML
    print("\nProcessing HTML...")
    html_file = Path('ui/main.html')
    if html_file.exists():
        modified, count = comment_tagged_logs(html_file)
        if modified:
            total_files += 1
            total_commented += count
            print(f'  ✓ main.html: {count} lines commented')
    
    print()
    print(f"Total: {total_files} files, {total_commented} debug lines commented out")
    print("\nNext: npm run build-webpack")
    print()

if __name__ == '__main__':
    main()

