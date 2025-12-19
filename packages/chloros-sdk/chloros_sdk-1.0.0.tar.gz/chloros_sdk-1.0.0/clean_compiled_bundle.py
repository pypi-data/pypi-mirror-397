#!/usr/bin/env python3
"""
Clean debug console logs from the COMPILED webpack bundle.
This is safer than trying to parse TypeScript multi-line statements.
"""

import re
from pathlib import Path

def clean_bundle(filepath):
    """Remove debug console statements from compiled JavaScript"""
    try:
        print(f"Reading {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        original_size = len(content)
        
        # Tags to remove
        debug_patterns = [
            r'\[DEBUG\]',
            r'\[ELECTRON PROGRESS\]',
            r'\[FILE-BROWSER\]',
            r'\[PROGRESS BAR\]',
            r'\[Progress Bar\]',
            r'\[ProgressBar',
            r'\[TAB-RENDER\]',
            r'\[SETTINGS\]',
            r'\[TIMEZONE\]',
            r'\[UPDATE-CHECKER\]',
            r'\[PROCESS BUTTON\]',
            r'\[SANDBOX\]',
            r'DEBUG\] ProgressBar',
            r'PRESERVE IMAGE-VIEWER',
            r'SELECTIVE CACHE CLEARING',
        ]
        
        print("Removing tagged console statements...")
        
        # Remove console.log/debug/info/warn statements with debug tags
        # These are typically: console.log('...', ...) or console.log(`...`, ...)
        for pattern in debug_patterns:
            # Match console statement with this tag
            content = re.sub(
                rf'console\.(log|debug|info|warn)\([^)]*{pattern}[^)]*\)',
                '(void 0)',  # Replace with no-op
                content,
                flags=re.IGNORECASE
            )
        
        new_size = len(content)
        saved = original_size - new_size
        
        if content != original:
            # Backup
            backup_path = str(filepath) + '.pre_bundle_cleanup'
            print(f"Creating backup: {backup_path}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
            
            # Write cleaned version
            print(f"Writing cleaned bundle...")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Cleaned! Saved {saved:,} bytes ({saved/1024:.1f} KB)")
            return True, saved
        else:
            print("No debug statements found to remove")
            return False, 0
    except Exception as e:
        print(f'✗ Error: {e}')
        return False, 0

def main():
    print("=" * 70)
    print("Clean Compiled Webpack Bundle")
    print("=" * 70)
    print()
    
    bundle_path = Path('ui/js/components-bundle.js')
    
    if not bundle_path.exists():
        print(f"❌ Bundle not found: {bundle_path}")
        return
    
    modified, saved = clean_bundle(bundle_path)
    
    print()
    if modified:
        print("✅ Bundle cleaned successfully!")
        print(f"💾 Saved {saved/1024:.1f} KB by removing debug logs")
    else:
        print("ℹ️  No changes needed")
    print()

if __name__ == '__main__':
    main()

