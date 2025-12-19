#!/usr/bin/env python3
"""
Final comprehensive cleanup of all remaining debug prints
"""

import os
import re
import warnings

# Patterns to remove from frontend
FRONTEND_PATTERNS = [
    r'console\.log\([^)]*\[DEBUG\] Progress bar LOCKED[^)]*\);?',
    r'console\.log\([^)]*\[DEBUG\] 🔴 phaseName setter[^)]*\);?',
    r'console\.log\([^)]*\[PROGRESS BAR\] 🔄[^)]*\);?',
    r'console\.log\([^)]*\[FILE-BROWSER\][^)]*\);?',
    r'console\.log\([^)]*\[Progress Bar\] Translated[^)]*\);?',
    r'console\.log\([^)]*\[DEBUG\] 🖼️ CACHE-BUST:[^)]*\);?',
]

# Files to clean
FRONTEND_FILES = [
    'ui/ts/progress-bar.ts',
    'ui/js/progress-bar.js',
    'ui/ts/file-browser.ts',
    'ui/js/file-browser.js',
    'ui/ts/image-viewer.ts',
    'ui/js/image-viewer.js',
    'resources/backend/ui/ts/progress-bar.ts',
    'resources/backend/ui/js/progress-bar.js',
    'resources/backend/ui/ts/file-browser.ts',
    'resources/backend/ui/js/file-browser.js',
    'resources/backend/ui/ts/image-viewer.ts',
    'resources/backend/ui/js/image-viewer.js',
]

def remove_console_logs_from_file(filepath, patterns):
    """Remove console.log statements matching patterns"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        removed_count = 0
        
        # Remove each pattern
        for pattern in patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            removed_count += len(matches)
            content = re.sub(pattern, '', content)
        
        # Also remove line-by-line for multi-line console.logs
        lines = content.split('\n')
        cleaned_lines = []
        skip_until_semicolon = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for debug patterns
            should_skip = False
            for check in ['[DEBUG] Progress bar LOCKED', '[DEBUG] 🔴 phaseName', 
                         '[PROGRESS BAR] 🔄', '[FILE-BROWSER]', '[Progress Bar] Translated',
                         '[DEBUG] 🖼️ CACHE-BUST:']:
                if check in line and 'console.log' in line:
                    should_skip = True
                    # Check if it's multi-line
                    if not line.strip().endswith(');'):
                        skip_until_semicolon = True
                    break
            
            if skip_until_semicolon:
                if ');' in line:
                    skip_until_semicolon = False
                i += 1
                continue
                
            if should_skip:
                removed_count += 1
                i += 1
                continue
            
            cleaned_lines.append(line)
            i += 1
        
        content = '\n'.join(cleaned_lines)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return removed_count
        return 0
    except FileNotFoundError:
        return -1
    except Exception as e:
        print(f'  ❌ Error: {e}')
        return -1

def suppress_ray_warnings():
    """Add warning suppression to tasks.py for Ray warnings"""
    filepath = 'tasks.py'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already suppressed
        if 'filterwarnings' in content and 'ray.worker.global_worker' in content:
            return 0
        
        # Add warning suppression after imports
        import_section_end = content.find('import threading')
        if import_section_end == -1:
            import_section_end = content.find('import traceback')
        
        if import_section_end != -1:
            # Find end of that line
            line_end = content.find('\n', import_section_end)
            
            warning_suppression = '''
# Suppress Ray deprecation warnings in production
import warnings
warnings.filterwarnings('ignore', message='.*ray.worker.global_worker.*')
warnings.filterwarnings('ignore', message='.*SIGTERM handler.*')
'''
            
            content = content[:line_end+1] + warning_suppression + content[line_end+1:]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        return 0
    except Exception as e:
        print(f'  ❌ Error in tasks.py: {e}')
        return 0

def remove_preview_cache_prints():
    """Remove [PREVIEW CACHE] prints from backend_server.py"""
    filepath = 'backend_server.py'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            if '[PREVIEW CACHE]' in line and 'print' in line:
                removed_count += 1
                continue
            cleaned_lines.append(line)
        
        if removed_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
        
        return removed_count
    except Exception as e:
        print(f'  ❌ Error in backend_server.py: {e}')
        return 0

print("=" * 70)
print("COMPREHENSIVE DEBUG CLEANUP")
print("=" * 70)
print()

# Clean frontend files
print("🧹 Cleaning frontend files...")
total_frontend = 0
for filepath in FRONTEND_FILES:
    count = remove_console_logs_from_file(filepath, FRONTEND_PATTERNS)
    if count > 0:
        print(f'  ✅ {filepath}: {count} statements removed')
        total_frontend += count
    elif count == -1:
        print(f'  ⏭️  {filepath}: not found')

print(f'\n📊 Frontend: {total_frontend} debug statements removed')

# Clean backend files
print("\n🧹 Cleaning backend files...")
preview_count = remove_preview_cache_prints()
if preview_count > 0:
    print(f'  ✅ backend_server.py: {preview_count} [PREVIEW CACHE] prints removed')

ray_warnings = suppress_ray_warnings()
if ray_warnings > 0:
    print(f'  ✅ tasks.py: Added Ray warning suppression')

print("\n" + "=" * 70)
print(f"✅ CLEANUP COMPLETE!")
print(f"   Frontend: {total_frontend} prints removed")
print(f"   Backend: {preview_count} prints removed + warnings suppressed")
print("=" * 70)









