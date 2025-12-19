#!/usr/bin/env python3
"""
Aggressive cleanup of ALL tagged debug console logs.
Handles single-line, multi-line, and template literals.
"""

import re
from pathlib import Path

def clean_file_aggressive(filepath):
    """Remove all console.log/debug/info/warn with debug tags"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Tags that indicate debug logging
        debug_indicators = [
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
            r'\[🔧\]',
            r'\[🔍\]',
            r'\[🚀\]',
            r'\[🎨\]',
            r'\[🔌\]',
            r'\[📦\]',
            r'\[✅\]',
            r'\[🔄\]',
            r'\[🖼️\]',
        ]
        
        pattern = '|'.join(debug_indicators)
        
        # Remove single-line console statements with tags
        content = re.sub(
            rf'^\s*console\.(log|debug|info|warn)\s*\([^)]*({pattern})[^;]*\);\s*$',
            '',
            content,
            flags=re.MULTILINE
        )
        
        # Remove multi-line console statements with tags (up to 10 lines)
        for i in range(10):
            content = re.sub(
                rf'^\s*console\.(log|debug|info|warn)\s*\([^)]*({pattern})[^\n]*\n(?:[^\n)]*\n)*?[^\n)]*\);\s*$',
                '',
                content,
                flags=re.MULTILINE
            )
        
        if content != original_content:
            # Backup
            backup_path = str(filepath) + '.pre_aggressive_cleanup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            removed = original_content.count('console.') - content.count('console.')
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Aggressive Tagged Debug Log Removal")
    print("=" * 70)
    print()
    
    files_modified = 0
    logs_removed = 0
    
    # Process TypeScript files
    print("Processing TypeScript files...")
    ts_dir = Path('ui/ts')
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name and '.backup' not in str(ts_file):
            modified, removed = clean_file_aggressive(ts_file)
            if modified:
                files_modified += 1
                logs_removed += removed
                print(f'  ✓ {ts_file.name}: {removed} logs')
    
    # Process HTML
    print("\nProcessing HTML...")
    html_file = Path('ui/main.html')
    if html_file.exists():
        modified, removed = clean_file_aggressive(html_file)
        if modified:
            files_modified += 1
            logs_removed += removed
            print(f'  ✓ main.html: {removed} logs')
    
    print()
    print(f"Modified {files_modified} files, removed ~{logs_removed} tagged console statements")
    print("\nRun: npm run build-webpack")
    print()

if __name__ == '__main__':
    main()

