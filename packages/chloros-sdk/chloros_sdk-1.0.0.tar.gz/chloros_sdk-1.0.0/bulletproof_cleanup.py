#!/usr/bin/env python3
"""
Bulletproof console cleanup for TypeScript.
Only removes simple single-line console statements.
Leaves complex/multi-line statements alone to avoid breaking anything.
"""

import re
from pathlib import Path

def bulletproof_cleanup(code):
    """
    Only replace simple, complete console statements on a single line.
    Syntax: console.log(stuff); or console.log(stuff)
    """
    lines = code.split('\n')
    result = []
    
    for line in lines:
        # Only process if it's a simple, complete console statement on one line
        # Must match: optional whitespace + console.method(...) + optional semicolon + optional whitespace + end
        if re.match(r'^\s*console\.(log|debug|info|warn)\([^)]*\)\s*;?\s*$', line):
            # Simple single-line statement - safe to remove
            indent = len(line) - len(line.lstrip())
            # Replace with empty comment to maintain line numbers for debugging
            result.append(' ' * indent + '// [Removed for production]')
        else:
            # Keep everything else unchanged
            result.append(line)
    
    return '\n'.join(result)

def process_file(filepath):
    """Process one TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if 'console.' not in original:
            return False, 0
        
        cleaned = bulletproof_cleanup(original)
        
        # Count removals
        original_consoles = len(re.findall(r'^\s*console\.(log|debug|info|warn)\([^)]*\)\s*;?\s*$', original, re.MULTILINE))
        cleaned_consoles = len(re.findall(r'^\s*console\.(log|debug|info|warn)\([^)]*\)\s*;?\s*$', cleaned, re.MULTILINE))
        removed = original_consoles - cleaned_consoles
        
        if cleaned != original and removed > 0:
            # Backup
            backup_path = str(filepath) + '.safe_backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Bulletproof TypeScript Console Cleanup")
    print("Only removes simple single-line statements - 100% safe")
    print("=" * 70)
    print()
    
    ts_dir = Path('ui/ts')
    modified_count = 0
    total_removed = 0
    
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            modified, removed = process_file(ts_file)
            if modified:
                modified_count += 1
                total_removed += removed
                print(f'✓ {ts_file.name}: {removed} simple statements removed')
    
    print()
    print(f"Modified: {modified_count} files")
    print(f"Removed: {total_removed} simple console statements")
    print(f"Note: Multi-line console statements left intact for safety")
    print()
    print("Next step: Run 'npm run build-webpack' to compile and verify")
    print()

if __name__ == '__main__':
    main()

