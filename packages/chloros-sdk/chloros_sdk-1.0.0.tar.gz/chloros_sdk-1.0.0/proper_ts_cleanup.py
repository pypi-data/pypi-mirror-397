#!/usr/bin/env python3
"""
Proper TypeScript console cleanup that handles multi-line statements correctly.
Removes entire console.log/debug/info/warn statements including multi-line calls.
"""

import re
from pathlib import Path

def remove_console_statements(code):
    """
    Remove console.log/debug/info/warn statements, preserving console.error.
    Handles both single-line and multi-line statements properly.
    """
    # Pattern to match console statements (but not console.error)
    # This regex handles multi-line statements with proper parentheses matching
    pattern = r'\bconsole\.(log|debug|info|warn)\s*\([^;]*?\)\s*;?'
    
    # For multi-line, we need a more complex approach
    lines = code.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if line starts a console statement (not console.error)
        match = re.search(r'\bconsole\.(log|debug|info|warn)\s*\(', line)
        
        if match and 'console.error' not in line:
            # Found a console statement
            # Check if it's complete on this line
            stripped = line.strip()
            
            # Count parentheses to see if statement is complete
            open_parens = line.count('(') - line.count(')')
            
            if open_parens == 0 and (stripped.endswith(';') or stripped.endswith(')')):
                # Complete single-line statement - skip it
                i += 1
                continue
            else:
                # Multi-line statement - need to find the end
                # Skip lines until we balance the parentheses
                paren_count = open_parens
                i += 1
                
                while i < len(lines) and paren_count > 0:
                    next_line = lines[i]
                    paren_count += next_line.count('(') - next_line.count(')')
                    i += 1
                
                # Entire multi-line statement is now skipped
                continue
        else:
            # Not a console statement or is console.error, keep it
            result.append(line)
            i += 1
    
    return '\n'.join(result)

def process_typescript_file(filepath):
    """Process a single TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if 'console.' not in original:
            return False, 0
        
        # Count console statements before
        before_count = len(re.findall(r'\bconsole\.(log|debug|info|warn)', original))
        
        cleaned = remove_console_statements(original)
        
        # Count after
        after_count = len(re.findall(r'\bconsole\.(log|debug|info|warn)', cleaned))
        removed = before_count - after_count
        
        if cleaned != original:
            # Save backup
            backup = str(filepath) + '.pre_proper_cleanup'
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            return True, removed
        
        return False, 0
    except Exception as e:
        print(f'✗ Error in {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Proper TypeScript Console Cleanup")
    print("Removes entire console statements including multi-line")
    print("=" * 70)
    print()
    
    ts_dir = Path('ui/ts')
    files_modified = 0
    total_removed = 0
    
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            modified, removed = process_typescript_file(ts_file)
            if modified:
                files_modified += 1
                total_removed += removed
                print(f'✓ {ts_file.name}: {removed} console statements removed')
    
    print()
    print(f"Modified {files_modified} files, removed {total_removed} statements")
    print()
    print("Next: Run 'npm run build-webpack' to compile")
    print()

if __name__ == '__main__':
    main()

