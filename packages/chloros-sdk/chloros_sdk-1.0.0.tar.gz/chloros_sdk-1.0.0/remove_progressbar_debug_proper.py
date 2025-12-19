#!/usr/bin/env python3
"""Properly remove all [DEBUG] ProgressBar: debug statements including their parameters"""

import re

def remove_console_logs(content):
    """Remove console.log statements with [DEBUG] ProgressBar: pattern"""
    lines = content.split('\n')
    result = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a console.log with [DEBUG] ProgressBar
        if 'console.log' in line and '[DEBUG] ProgressBar:' in line:
            # Check if it's a single-line console.log
            if line.strip().endswith(');'):
                # Single line console.log - just skip it
                removed_count += 1
                i += 1
                continue
            else:
                # Multi-line console.log - skip until we find the closing );
                removed_count += 1
                paren_count = line.count('(') - line.count(')')
                i += 1
                while i < len(lines) and paren_count > 0:
                    paren_count += lines[i].count('(') - lines[i].count(')')
                    i += 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result), removed_count

files_to_clean = [
    'ui/ts/progress-bar.ts',
]

total_removed = 0

for file_path in files_to_clean:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content, removed_count = remove_console_logs(content)
        
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f'✅ Removed {removed_count} debug statements from {file_path}')
            total_removed += removed_count
        else:
            print(f'✓ No debug statements in {file_path}')
    except FileNotFoundError:
        print(f'⏭️  Skipped (not found): {file_path}')
    except Exception as e:
        print(f'❌ Error processing {file_path}: {e}')

print(f'\n✅ Total removed: {total_removed} [DEBUG] ProgressBar: statements')

