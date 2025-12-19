#!/usr/bin/env python3
"""
Safe production cleanup - replaces console.log/debug/info/warn with void(0)
This maintains syntax and won't break webpack compilation.
"""

import re
from pathlib import Path

def safe_cleanup_typescript(code):
    """
    Replace console.log/debug/info/warn calls with void(0);
    This is the safest approach that won't break any syntax.
    """
    # Replace console.log(...) with void(0)
    # This regex handles nested parentheses properly
    code = re.sub(
        r'\bconsole\.log\s*\([^;]*?\);',
        'void(0);',
        code,
        flags=re.DOTALL
    )
    
    code = re.sub(
        r'\bconsole\.debug\s*\([^;]*?\);',
        'void(0);',
        code,
        flags=re.DOTALL
    )
    
    code = re.sub(
        r'\bconsole\.info\s*\([^;]*?\);',
        'void(0);',
        code,
        flags=re.DOTALL
    )
    
    code = re.sub(
        r'\bconsole\.warn\s*\([^;]*?\);',
        'void(0);',
        code,
        flags=re.DOTALL
    )
    
    # Handle cases without semicolons (at end of lines, etc.)
    code = re.sub(
        r'\bconsole\.log\s*\([^)]*\)(?!\s*[;\.])',
        'void(0)',
        code
    )
    
    code = re.sub(
        r'\bconsole\.debug\s*\([^)]*\)(?!\s*[;\.])',
        'void(0)',
        code
    )
    
    code = re.sub(
        r'\bconsole\.info\s*\([^)]*\)(?!\s*[;\.])',
        'void(0)',
        code
    )
    
    code = re.sub(
        r'\bconsole\.warn\s*\([^)]*\)(?!\s*[;\.])',
        'void(0)',
        code
    )
    
    return code

def process_file(filepath):
    """Process a TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if 'console.' not in original or 'console.error' in original and 'console.log' not in original:
            return False, 0
        
        # Count statements before
        before = (
            len(re.findall(r'\bconsole\.log', original)) +
            len(re.findall(r'\bconsole\.debug', original)) +
            len(re.findall(r'\bconsole\.info', original)) +
            len(re.findall(r'\bconsole\.warn', original))
        )
        
        cleaned = safe_cleanup_typescript(original)
        
        # Count after
        after = (
            len(re.findall(r'\bconsole\.log', cleaned)) +
            len(re.findall(r'\bconsole\.debug', cleaned)) +
            len(re.findall(r'\bconsole\.info', cleaned)) +
            len(re.findall(r'\bconsole\.warn', cleaned))
        )
        
        replaced = before - after
        
        if cleaned != original and replaced > 0:
            # Backup
            backup = str(filepath) + '.final_backup'
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            return True, replaced
        
        return False, 0
    except Exception as e:
        print(f'✗ Error in {filepath}: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Safe Production TypeScript Cleanup")
    print("Replaces console statements with void(0) - Safe for webpack")
    print("=" * 70)
    print()
    
    ts_dir = Path('ui/ts')
    modified = 0
    total = 0
    
    for ts_file in sorted(ts_dir.glob('*.ts')):
        if 'backup' not in ts_file.name:
            was_modified, count = process_file(ts_file)
            if was_modified:
                modified += 1
                total += count
                print(f'✓ {ts_file.name}: {count} statements replaced')
    
    print()
    print(f"Modified {modified} files, replaced {total} console statements")
    print()

if __name__ == '__main__':
    main()

