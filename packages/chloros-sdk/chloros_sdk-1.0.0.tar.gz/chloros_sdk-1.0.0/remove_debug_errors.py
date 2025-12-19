#!/usr/bin/env python3
"""Remove console.error with [DEBUG] tags from TypeScript sources"""

import os

files_to_clean = [
    'ui/ts/image-viewer.ts',
    'ui/ts/file-browser.ts',
]

def remove_debug_errors(content):
    """Remove console.error/console.log lines with [DEBUG] tags"""
    lines = content.split('\n')
    result = []
    removed = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for console.error or console.log with [DEBUG]
        if ('[DEBUG]' in line) and ('console.error' in line or 'console.log' in line):
            # Skip this line and any continuation
            removed += 1
            # If multi-line, skip until closing
            if not (');' in line or line.strip().endswith(');')):
                paren_count = line.count('(') - line.count(')')
                i += 1
                while i < len(lines) and paren_count != 0:
                    paren_count += lines[i].count('(') - lines[i].count(')')
                    i += 1
                continue
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result), removed

total = 0
for filepath in files_to_clean:
    if not os.path.exists(filepath):
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned, count = remove_debug_errors(content)
        
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f'✅ {filepath}: {count} debug errors removed')
            total += count
    except Exception as e:
        print(f'❌ {filepath}: {e}')

print(f'\n✅ Total: {total} debug error statements removed')

