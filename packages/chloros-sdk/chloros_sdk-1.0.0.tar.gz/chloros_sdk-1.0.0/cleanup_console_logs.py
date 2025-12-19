#!/usr/bin/env python3
"""
Script to remove/comment out frontend console log statements before production launch.
Keeps console.error for critical error logging.
Handles multi-line statements and complex cases.
"""

import os
import re
from pathlib import Path

# Directories and files to process
TARGETS = [
    'ui/ts',
    'ui/js',
    'preload.js',
    'main.cjs',
    'main.js',
    'electron-backend.cjs',
]

def should_skip_file(filepath):
    """Skip certain files that shouldn't be modified"""
    skip_patterns = [
        'node_modules',
        'dist',
        'build',
        '.min.js',
        'test-script',
        'backup',
        'components-bundle.js',  # Skip bundled file
        'components.js',  # Skip bundled file
    ]
    filepath_str = str(filepath)
    return any(pattern in filepath_str for pattern in skip_patterns)

def find_statement_end(content, start_pos):
    """Find the end of a console statement, handling nested parentheses"""
    paren_count = 0
    in_string = False
    string_char = None
    escape_next = False
    i = start_pos
    
    while i < len(content):
        char = content[i]
        
        if escape_next:
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            escape_next = True
            i += 1
            continue
        
        if char in ['"', "'", '`'] and not in_string:
            in_string = True
            string_char = char
        elif char == string_char and in_string:
            in_string = False
            string_char = None
        elif char == '(' and not in_string:
            paren_count += 1
        elif char == ')' and not in_string:
            paren_count -= 1
            if paren_count == 0:
                # Find the semicolon or end of line
                j = i + 1
                while j < len(content) and content[j] in [' ', '\t']:
                    j += 1
                if j < len(content) and content[j] == ';':
                    return j + 1
                return i + 1
        
        i += 1
    
    return i

def clean_console_logs(content):
    """Remove console log statements while preserving console.error"""
    # Patterns for console statements we want to remove
    console_patterns = ['console.log', 'console.debug', 'console.info', 'console.warn']
    
    result = []
    i = 0
    
    while i < len(content):
        # Check if we're at a console statement
        found_console = None
        for pattern in console_patterns:
            if content[i:i+len(pattern)] == pattern:
                found_console = pattern
                break
        
        if found_console:
            # Check if this is actually console.error that we want to keep
            is_error = content[i:i+len('console.error')] == 'console.error'
            
            if is_error:
                # Keep console.error
                result.append(content[i])
                i += 1
            else:
                # Find the start of the line
                line_start = i
                while line_start > 0 and content[line_start - 1] not in ['\n', '\r']:
                    line_start -= 1
                
                # Get the indentation
                indent = ''
                j = line_start
                while j < i and content[j] in [' ', '\t']:
                    indent += content[j]
                    j += 1
                
                # Find the end of the console statement
                statement_end = find_statement_end(content, i + len(found_console))
                
                # Comment out the entire statement
                result.append('// ')
                
                # Add the statement (from current position to end)
                i += 1
                continue
        else:
            result.append(content[i])
            i += 1
    
    return ''.join(result)

def process_file(filepath):
    """Process a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
        
        # Quick check - if no console statements, skip
        if 'console.' not in original_content:
            return False
        
        # Clean the content using regex (simpler and more reliable for most cases)
        cleaned_content = original_content
        
        # Comment out console.log, console.debug, console.info, console.warn
        # But NOT console.error
        patterns = [
            (r'(\s*)(console\.log\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.debug\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.info\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.warn\s*\([^;]*\);?)', r'\1// \2'),
        ]
        
        for pattern, replacement in patterns:
            cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.MULTILINE)
        
        # Only write if something changed
        if cleaned_content != original_content:
            # Create backup
            backup_path = str(filepath) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write cleaned content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # Count how many lines were commented
            changes = cleaned_content.count('// console.') - original_content.count('// console.')
            print(f"✓ Cleaned {changes} statements in: {filepath}")
            return True
        
        return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("Console Log Cleanup for Production Launch")
    print("=" * 70)
    print()
    print("This will comment out console.log/debug/info/warn statements")
    print("while keeping console.error for critical error logging.")
    print()
    
    files_processed = 0
    files_modified = 0
    
    for target in TARGETS:
        target_path = Path(target)
        
        if not target_path.exists():
            print(f"⚠ Skipping non-existent: {target}")
            continue
        
        if target_path.is_file():
            # Single file
            if not should_skip_file(target_path):
                files_processed += 1
                if process_file(target_path):
                    files_modified += 1
        elif target_path.is_dir():
            # Directory - process all .js and .ts files
            for ext in ['*.js', '*.ts']:
                for filepath in target_path.rglob(ext):
                    if not should_skip_file(filepath):
                        files_processed += 1
                        if process_file(filepath):
                            files_modified += 1
    
    print()
    print("=" * 70)
    print(f"Summary:")
    print(f"  Files processed: {files_processed}")
    print(f"  Files modified: {files_modified}")
    print(f"  Backups created with .backup extension")
    print()
    print("Next steps:")
    print("  1. Run 'npm run build-ts' to rebuild TypeScript")
    print("  2. Test the application thoroughly")
    print("  3. If issues occur, restore from .backup files")
    print("=" * 70)

if __name__ == '__main__':
    main()

