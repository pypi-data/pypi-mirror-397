import os
import re
from pathlib import Path

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if 'console.' not in content:
            return False
        
        original = content
        patterns = [
            (r'(\s*)(console\.log\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.debug\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.info\s*\([^;]*\);?)', r'\1// \2'),
            (r'(\s*)(console\.warn\s*\([^;]*\);?)', r'\1// \2'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if content != original:
            backup_path = str(filepath) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            changes = content.count('// console.') - original.count('// console.')
            print(f'✓ Cleaned {changes} statements in: {filepath}')
            return True
        return False
    except Exception as e:
        print(f'✗ Error: {filepath}: {e}')
        return False

resources_path = Path('resources/backend/ui')
if resources_path.exists():
    count = 0
    for ext in ['*.js']:
        for filepath in resources_path.rglob(ext):
            if 'node_modules' not in str(filepath) and 'components-bundle' not in str(filepath):
                if clean_file(filepath):
                    count += 1
    print(f'\nCleaned {count} files in resources/backend/ui')
else:
    print('resources/backend/ui does not exist')

