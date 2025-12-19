#!/usr/bin/env python3
"""Remove remaining debug prints: [PPK], [COORD-DEBUG], [DROPDOWN-CLICK], console.trace"""

import re

files_to_clean = {
    'ui/ts/image-viewer.ts': ['[PPK]', '[COORD-DEBUG]', '[DROPDOWN-CLICK]', 'console.trace'],
    'ui/ts/settings.ts': ['[PPK]', '[COORD-DEBUG]', '[DROPDOWN-CLICK]'],
}

def remove_console_log(content, patterns):
    """Remove console.log/console.trace statements containing any of the patterns"""
    lines = content.split('\n')
    result = []
    removed_count = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line should be removed
        should_remove = False
        for pattern in patterns:
            if pattern in line and ('console.log' in line or 'console.trace' in line or 'console.error' in line):
                should_remove = True
                break
        
        if should_remove:
            removed_count += 1
            # Check if multi-line
            if not (');' in line or line.strip().endswith(');\n') or line.strip().endswith(');')):
                # Multi-line - skip until closing
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
    
    return '\n'.join(result), removed_count

total_removed = 0

for filepath, patterns in files_to_clean.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned, count = remove_console_log(content, patterns)
        
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f'✅ {filepath}: {count} debug statements removed')
            total_removed += count
        else:
            print(f'✓ {filepath}: Already clean')
    
    except Exception as e:
        print(f'❌ {filepath}: {e}')

print(f'\n✅ Total: {total_removed} debug statements removed')









