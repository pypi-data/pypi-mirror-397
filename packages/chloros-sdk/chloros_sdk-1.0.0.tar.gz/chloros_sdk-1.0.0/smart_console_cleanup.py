#!/usr/bin/env python3
"""
Smart console log cleanup that handles multi-line statements properly.
Uses a state machine to track parentheses nesting.
"""

import re
from pathlib import Path

def remove_console_statements(content):
    """
    Remove console.log/debug/info/warn statements while preserving console.error.
    Handles multi-line statements by tracking parentheses.
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if line contains a console statement (but not console.error)
        if re.search(r'\bconsole\.(log|debug|info|warn)\s*\(', line) and 'console.error' not in line:
            # Found a console statement - need to find where it ends
            indent = len(line) - len(line.lstrip())
            indent_str = line[:indent]
            
            # Track parentheses to find the end
            paren_count = 0
            in_string = False
            string_char = None
            escape_next = False
            
            # Combine lines until we find the end of the statement
            combined = line
            j = i
            
            for char_idx, char in enumerate(combined):
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
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
                        # Found the end - check for semicolon
                        remaining = combined[char_idx+1:]
                        semicolon_match = re.match(r'^\s*;', remaining)
                        break
            
            # If parentheses are balanced, we found the complete statement
            if paren_count == 0:
                # Comment it out
                result.append(indent_str + '// ' + combined[indent:].lstrip())
                if j > i:
                    # Skip the additional lines we consumed
                    i = j + 1
                else:
                    i += 1
            else:
                # Multi-line statement - need to find more lines
                j = i + 1
                while j < len(lines) and paren_count > 0:
                    next_line = lines[j]
                    combined += '\n' + next_line
                    
                    for char in next_line:
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
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
                                break
                    
                    j += 1
                
                # Comment out all the lines
                statement_lines = combined.split('\n')
                for stmt_line in statement_lines:
                    line_indent = len(stmt_line) - len(stmt_line.lstrip())
                    line_indent_str = stmt_line[:line_indent]
                    result.append(line_indent_str + '// ' + stmt_line[line_indent:])
                
                i = j
        else:
            # Not a console statement, keep the line as is
            result.append(line)
            i += 1
    
    return '\n'.join(result)

def process_file(filepath):
    """Process a single TypeScript file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        if 'console.' not in original:
            return False
        
        cleaned = remove_console_statements(original)
        
        if cleaned != original:
            # Save backup
            backup = str(filepath) + '.backup2'
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            print(f'✓ Cleaned: {filepath}')
            return True
        
        return False
    except Exception as e:
        print(f'✗ Error in {filepath}: {e}')
        return False

def main():
    print("=" * 70)
    print("Smart Console Cleanup for TypeScript Files")
    print("=" * 70)
    print()
    
    ts_dir = Path('ui/ts')
    files_modified = 0
    
    for ts_file in ts_dir.glob('*.ts'):
        if 'backup' not in ts_file.name:
            if process_file(ts_file):
                files_modified += 1
    
    print()
    print(f"Modified {files_modified} TypeScript files")
    print("Backups saved with .backup2 extension")
    print()

if __name__ == '__main__':
    main()

