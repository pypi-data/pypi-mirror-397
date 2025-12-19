#!/usr/bin/env python3
"""
Clean up custom-tagged debug console logs from TypeScript and HTML files.
Targets patterns like: console.log('[DEBUG]...'), console.log('[ELECTRON PROGRESS]...'), etc.
"""

import re
from pathlib import Path

# Common debug tags to remove
DEBUG_TAGS = [
    'DEBUG',
    'ELECTRON PROGRESS',
    'FILE-BROWSER',
    'PROGRESS BAR',
    'Progress Bar',
    'ProgressBar',
    'TAB-RENDER',
    'SETTINGS',
    'UPDATE-CHECKER',
    'TIMEZONE',
    'PROCESS BUTTON',
    'SANDBOX',
    'PRESERVE IMAGE-VIEWER',
    'SELECTIVE CACHE CLEARING',
    'IMPORT PROCESS',
]

def clean_typescript_file(filepath):
    """Clean tagged console logs from TypeScript files"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Pattern to match console.log/debug/info/warn with debug tags
        # Matches: console.log('[TAG] ...'), console.log(`[TAG] ...`), etc.
        patterns = []
        for tag in DEBUG_TAGS:
            # Single line with string
            patterns.append(rf"^\s*console\.(log|debug|info|warn)\s*\(\s*['\"`]\[{tag}\][^)]*\)\s*;?\s*$")
            # Single line with template literal
            patterns.append(rf"^\s*console\.(log|debug|info|warn)\s*\(\s*`\[{tag}\][^)]*\)\s*;?\s*$")
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            should_remove = False
            for pattern in patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_remove = True
                    break
            
            if not should_remove:
                cleaned_lines.append(line)
            else:
                # Keep blank line to maintain line numbers
                cleaned_lines.append('')
        
        content = '\n'.join(cleaned_lines)
        
        if content != original:
            # Backup
            backup_path = str(filepath) + '.tagged_backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            removed = len(original.split('\n')) - len([l for l in cleaned_lines if l.strip()])
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False, 0

def clean_html_file(filepath):
    """Clean tagged console logs from HTML files (main.html)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Match console.log statements with [DEBUG], [ELECTRON PROGRESS], etc.
        # This handles both single and multi-line
        for tag in DEBUG_TAGS:
            # Simple single-line pattern
            content = re.sub(
                rf"^\s*console\.(log|debug|info|warn)\s*\(['\"`]\[{tag}\][^;]*\);\s*$",
                '',
                content,
                flags=re.MULTILINE | re.IGNORECASE
            )
        
        if content != original:
            # Backup
            backup_path = str(filepath) + '.tagged_backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            removed = original.count('console.') - content.count('console.')
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Custom Tagged Debug Log Cleanup")
    print("Removing [DEBUG], [ELECTRON PROGRESS], [FILE-BROWSER], etc.")
    print("=" * 70)
    print()
    
    total_files = 0
    total_removed = 0
    
    # Clean TypeScript files
    print("Cleaning TypeScript files...")
    ts_dir = Path('ui/ts')
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            modified, removed = clean_typescript_file(ts_file)
            if modified:
                total_files += 1
                total_removed += removed
                print(f'  ✓ {ts_file.name}: {removed} tagged logs removed')
    
    # Clean HTML file
    print("\nCleaning HTML files...")
    html_file = Path('ui/main.html')
    if html_file.exists():
        modified, removed = clean_html_file(html_file)
        if modified:
            total_files += 1
            total_removed += removed
            print(f'  ✓ main.html: ~{removed} tagged logs removed')
    
    print()
    print(f"Summary: Modified {total_files} files, removed ~{total_removed} tagged debug logs")
    print()
    print("Next: Run 'npm run build-webpack' to recompile")
    print()

if __name__ == '__main__':
    main()

