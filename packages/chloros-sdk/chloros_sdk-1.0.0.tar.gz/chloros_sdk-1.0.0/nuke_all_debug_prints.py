#!/usr/bin/env python3
"""
NUCLEAR OPTION: Remove ALL console.log statements with debug tags
from TypeScript source files, then rebuild webpack bundle.
"""

import re
import os

# All debug/trace patterns to remove (comprehensive list)
DEBUG_PATTERNS = [
    '[DEBUG]',
    '[PROGRESS BAR]',
    '[FILE-BROWSER]',
    '[TAB-RENDER]',
    '[SETTINGS]',
    '[TIMEZONE]',
    '[UPDATE-CHECKER]',
    '[PROCESS BUTTON]',
    '[IMAGE-VIEWER]',
    '[BACKEND-STATUS]',
    '[SSE]',
    '[Progress Bar]',
    '[PREVIEW CACHE]',
    '🔧', '🔍', '🚀', '🎨', '🔌', '📦', '✅', '🔄', '🖼️', '⏳',
    '🔴', '🔓', '🎯', '🔥', '⚡', '📁', '🔔', '🧹',
]

def should_remove_line(line):
    """Check if a console.log line should be removed"""
    if 'console.log' not in line:
        return False
    
    # Check if console.error (keep these)
    if 'console.error' in line or 'console.warn' in line:
        return False
    
    # Remove if it contains any debug pattern
    for pattern in DEBUG_PATTERNS:
        if pattern in line:
            return True
    
    return False

def remove_debug_console_logs(content):
    """Remove console.log statements with debug patterns, handling multi-line"""
    lines = content.split('\n')
    result = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        if should_remove_line(line):
            # This console.log should be removed
            # Check if it's multi-line (doesn't end with );)
            if line.strip().endswith(');') or line.strip().endswith(');'):
                # Single line - skip it
                removed_count += 1
                i += 1
                continue
            else:
                # Multi-line - skip until we find the closing );
                removed_count += 1
                paren_count = line.count('(') - line.count(')')
                i += 1
                while i < len(lines) and paren_count != 0:
                    paren_count += lines[i].count('(') - lines[i].count(')')
                    i += 1
                continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result), removed_count

# TypeScript source files to clean
files_to_clean = [
    'ui/ts/progress-bar.ts',
    'ui/ts/file-browser.ts',
    'ui/ts/image-viewer.ts',
    'ui/ts/image-tabs.ts',
    'ui/ts/settings-panel.ts',
    'ui/ts/sse-client.ts',
]

print("=" * 80)
print("NUCLEAR DEBUG CLEANUP - Removing ALL Debug Console.log Statements")
print("=" * 80)
print()

total_removed = 0

for filepath in files_to_clean:
    if not os.path.exists(filepath):
        print(f'⏭️  Skipped (not found): {filepath}')
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content, count = remove_debug_console_logs(content)
        
        if count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f'✅ {filepath}: {count} debug console.logs removed')
            total_removed += count
        else:
            print(f'✓ {filepath}: Already clean')
    except Exception as e:
        print(f'❌ {filepath}: Error - {e}')

print()
print("=" * 80)
print(f"✅ TOTAL: {total_removed} debug console.log statements removed")
print("=" * 80)
print()
print("Next: Rebuild webpack bundle with 'npm run build-webpack'")
print()

