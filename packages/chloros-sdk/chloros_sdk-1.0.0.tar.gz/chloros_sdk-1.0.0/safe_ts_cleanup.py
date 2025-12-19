#!/usr/bin/env python3
"""
Safe TypeScript console cleanup - only comments out complete single-line statements
"""

import re
from pathlib import Path

def safe_clean_typescript(content):
    """
    Safely clean console statements from TypeScript.
    Only handles simple single-line cases to avoid syntax errors.
    """
    lines = content.split('\n')
    result = []
    
    for line in lines:
        # Check if this line contains a complete console statement
        # Must be: console.log/debug/info/warn(...); on a single line
        if re.search(r'\bconsole\.(log|debug|info|warn)\s*\([^)]*\)\s*;?\s*$', line) and 'console.error' not in line:
            # Get the indentation
            indent = len(line) - len(line.lstrip())
            indent_str = line[:indent]
            # Comment it out
            result.append(indent_str + '// ' + line[indent:])
        else:
            # Keep line as-is (including multi-line console statements)
            result.append(line)
    
    return '\n'.join(result)

def process_ts_file(filepath):
    """Process a TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if 'console.' not in original:
            return False, 0
        
        cleaned = safe_clean_typescript(original)
        
        if cleaned != original:
            # Count changes
            changes = cleaned.count('// console.') - original.count('// console.')
            
            # Save backup
            backup = str(filepath) + '.clean_backup'
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            return True, changes
        
        return False, 0
    except Exception as e:
        print(f'✗ Error in {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Safe TypeScript Console Cleanup")
    print("Only cleans simple single-line console statements")
    print("=" * 70)
    print()
    
    ts_dir = Path('ui/ts')
    files_modified = 0
    total_changes = 0
    
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            modified, changes = process_ts_file(ts_file)
            if modified:
                files_modified += 1
                total_changes += changes
                print(f'✓ {ts_file.name}: {changes} statements cleaned')
    
    print()
    print(f"Modified {files_modified} files, cleaned {total_changes} statements")
    print()

if __name__ == '__main__':
    main()

