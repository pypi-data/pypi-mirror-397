#!/usr/bin/env python3
"""
Safe cleanup of debug prints - preserves code structure
"""

import re

def safe_remove_console_logs(content, keywords):
    """Safely remove console.log statements containing any of the keywords"""
    lines = content.split('\n')
    result = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line contains console.log with any of our keywords
        has_keyword = False
        if 'console.log' in line:
            for keyword in keywords:
                if keyword in line:
                    has_keyword = True
                    break
        
        if has_keyword:
            # This is a console.log we want to remove
            # Check if it's complete on one line
            if line.count('(') == line.count(')'):
                # Single line - just skip it
                removed_count += 1
                i += 1
                continue
            else:
                # Multi-line - skip until balanced
                paren_count = line.count('(') - line.count(')')
                removed_count += 1
                i += 1
                while i < len(lines) and paren_count != 0:
                    paren_count += lines[i].count('(') - lines[i].count(')')
                    i += 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result), removed_count

# Frontend keywords to remove
FRONTEND_KEYWORDS = [
    '[DEBUG] Progress bar LOCKED',
    '[DEBUG] 🔴 phaseName',
    '[PROGRESS BAR] 🔄',
    '[FILE-BROWSER]',
    '[Progress Bar] Translated',
    '[DEBUG] 🖼️ CACHE-BUST:',
]

# Files to clean
files_to_clean = {
    'ui/ts/progress-bar.ts': FRONTEND_KEYWORDS,
    'ui/ts/file-browser.ts': FRONTEND_KEYWORDS,
    'ui/ts/image-viewer.ts': FRONTEND_KEYWORDS,
}

print("=" * 70)
print("SAFE DEBUG CLEANUP - TypeScript Sources Only")
print("=" * 70)
print()

total_removed = 0

for filepath, keywords in files_to_clean.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content, count = safe_remove_console_logs(content, keywords)
        
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f'✅ {filepath}: {count} debug statements removed')
            total_removed += count
        else:
            print(f'✓ {filepath}: No matching debug statements')
    except Exception as e:
        print(f'❌ {filepath}: Error - {e}')

# Backend cleanup
print("\n" + "=" * 70)
print("Backend Cleanup")
print("=" * 70)

# Remove [PREVIEW CACHE] prints
try:
    with open('backend_server.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned = []
    backend_removed = 0
    for line in lines:
        if '[PREVIEW CACHE]' in line and 'print' in line:
            backend_removed += 1
            continue
        cleaned.append(line)
    
    if backend_removed > 0:
        with open('backend_server.py', 'w', encoding='utf-8') as f:
            f.writelines(cleaned)
        print(f'✅ backend_server.py: {backend_removed} [PREVIEW CACHE] prints removed')
    else:
        print(f'✓ backend_server.py: No [PREVIEW CACHE] prints found')
except Exception as e:
    print(f'❌ backend_server.py: Error - {e}')

# Add warning suppression to tasks.py
try:
    with open('tasks.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has warning suppression
    if 'filterwarnings' in content and 'global_worker' in content:
        print('✓ tasks.py: Warning suppression already present')
    else:
        # Add after import warnings line if it exists
        if 'import warnings' in content:
            lines = content.split('\n')
            result = []
            added = False
            for line in lines:
                result.append(line)
                if 'import warnings' in line and not added:
                    result.append("warnings.filterwarnings('ignore', message='.*ray.worker.global_worker.*')")
                    result.append("warnings.filterwarnings('ignore', category=DeprecationWarning, module='ray')")
                    added = True
            
            with open('tasks.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            print('✅ tasks.py: Added Ray warning suppression')
        else:
            print('⚠️  tasks.py: No warnings import found')
except Exception as e:
    print(f'❌ tasks.py: Error - {e}')

print("\n" + "=" * 70)
print(f"✅ CLEANUP COMPLETE - {total_removed} frontend prints removed")
print("=" * 70)

