#!/usr/bin/env python3
"""Remove all [DEBUG] ProgressBar: debug statements"""

import re

files_to_clean = [
    'ui/ts/progress-bar.ts',
    'ui/js/progress-bar.js',
    'resources/backend/ui/js/progress-bar.js',
    'resources/backend/ui/ts/progress-bar.ts',
]

total_removed = 0

for file_path in files_to_clean:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove lines with [DEBUG] ProgressBar:
        lines = content.split('\n')
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            if '[DEBUG] ProgressBar:' in line and 'console.log' in line:
                removed_count += 1
                continue
            cleaned_lines.append(line)
        
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cleaned_lines))
            print(f'✅ Removed {removed_count} debug statements from {file_path}')
            total_removed += removed_count
        else:
            print(f'✓ No debug statements in {file_path}')
    except FileNotFoundError:
        print(f'⏭️  Skipped (not found): {file_path}')
    except Exception as e:
        print(f'❌ Error processing {file_path}: {e}')

print(f'\n✅ Total removed: {total_removed} [DEBUG] ProgressBar: statements')

