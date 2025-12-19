#!/usr/bin/env python3
"""
ULTIMATE DEBUG NUKE - Remove ALL console.log statements with ANY debug pattern
Comprehensive cleanup across all TypeScript sources
"""

import re
import os
from pathlib import Path

# ALL patterns to remove (comprehensive list)
DEBUG_PATTERNS = [
    '[DEBUG]', '[PROGRESS BAR]', '[FILE-BROWSER]', '[TAB-RENDER]', 
    '[SETTINGS]', '[TIMEZONE]', '[UPDATE-CHECKER]', '[PROCESS BUTTON]',
    '[IMAGE-VIEWER]', '[BACKEND-STATUS]', '[SSE]', '[Progress Bar]',
    '[PREVIEW CACHE]', '[DETECTING]', '[ANALYZING]', '[CALIBRATING]',
    '[EXPORTING]', '[FILE-PANEL]', '[PROGRESS BAR VERSION]',
    # Emoji patterns
    '🔧', '🔍', '🚀', '🎨', '🔌', '📦', '✅', '🔄', '🖼️', '⏳',
    '🔴', '🔓', '🎯', '🔥', '⚡', '📁', '🔔', '🧹', '👤', '🖥️',
]

def should_remove_console_log(line):
    """Check if this console.log should be removed"""
    if 'console.log' not in line and 'console.error' not in line:
        return False
    
    # Keep console.warn (important warnings)
    if 'console.warn' in line:
        return False
    
    # Remove if it contains ANY debug pattern
    for pattern in DEBUG_PATTERNS:
        if pattern in line:
            return True
    
    return False

def remove_multi_line_console(lines, start_idx):
    """Remove a multi-line console.log/error statement"""
    paren_count = lines[start_idx].count('(') - lines[start_idx].count(')')
    i = start_idx + 1
    
    while i < len(lines) and paren_count != 0:
        paren_count += lines[i].count('(') - lines[i].count(')')
        i += 1
    
    return i

def clean_typescript_file(filepath):
    """Remove all debug console.logs from a TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        removed_count = 0
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if should_remove_console_log(line):
                # This line should be removed
                removed_count += 1
                
                # Check if it's multi-line
                if not (');' in line or line.strip().endswith(');\n')):
                    # Multi-line - skip all lines until closing
                    i = remove_multi_line_console(lines, i)
                else:
                    # Single line - skip it
                    i += 1
                continue
            
            cleaned_lines.append(line)
            i += 1
        
        if removed_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return removed_count
        
        return 0
    
    except Exception as e:
        print(f'❌ Error processing {filepath}: {e}')
        return 0

# Find ALL TypeScript files
typescript_files = list(Path('ui/ts').rglob('*.ts'))

print("=" * 80)
print("ULTIMATE DEBUG NUKE - Removing ALL Debug Console Logs")
print("=" * 80)
print()

total_removed = 0
files_cleaned = 0

for ts_file in typescript_files:
    count = clean_typescript_file(str(ts_file))
    if count > 0:
        print(f'✅ {ts_file}: {count} debug statements removed')
        total_removed += count
        files_cleaned += 1
    else:
        print(f'✓ {ts_file}: Already clean')

print()
print("=" * 80)
print(f"✅ TOTAL: {total_removed} statements removed from {files_cleaned} files")
print("=" * 80)
print()

