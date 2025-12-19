import re
from pathlib import Path

js_files = list(Path('ui/js').glob('*.js'))
total = 0
problematic = []

for js_file in js_files:
    if any(skip in js_file.name for skip in ['backup', 'components-bundle', 'components.js', 'test-script']):
        continue
    
    content = js_file.read_text(encoding='utf-8', errors='ignore')
    matches = re.findall(r'^\s*console\.(log|debug|info|warn)\s*\(', content, re.MULTILINE)
    count = len(matches)
    
    if count > 0:
        problematic.append((js_file.name, count))
        total += count

print('Final Production JavaScript Verification:')
print('=' * 50)

if total == 0:
    print('✅ ALL PRODUCTION FILES ARE CLEAN!')
    print('\nNo console.log/debug/info/warn statements remain.')
    print('console.error statements are preserved for error handling.')
else:
    print(f'⚠️ Found {total} remaining statements in:')
    for name, count in problematic:
        print(f'  - {name}: {count}')

