#!/usr/bin/env python3
"""
Clean up documentation - keep only essential, current docs
"""

from pathlib import Path
import shutil

# KEEP THESE - Essential current documentation
KEEP_DOCS = {
    # Core documentation
    'README.md',
    'LICENSE',
    'THIRD-PARTY-NOTICES',
    
    # Current summaries (from this session)
    'FILE_RESTORATION_COMPLETE.md',
    'FINAL_CLEANUP_SUMMARY.md',
    'CONSOLE_CLEANUP_SUMMARY.md',
    
    # Essential user guides
    'docs/CHLOROS_CLI_USER_GUIDE.md',
    'docs/CHLOROS_CLI_QUICK_START.md',
    'docs/AUTHENTICATION_GUIDE.md',
    'docs/BUILD_INSTRUCTIONS.md',
    'docs/CODE_SIGNING_GUIDE.md',
    'docs/SYSTEM_REQUIREMENTS.md',
    'docs/WORKSPACE_RECOVERY_GUIDE.md',
    
    # API documentation
    'docs/CHLOROS_API_DOCUMENTATION_INDEX.md',
    'docs/CHLOROS_API_QUICK_START.md',
    'docs/CHLOROS_API_EXECUTIVE_SUMMARY.md',
    
    # Important technical docs
    'docs/BACKEND_DEBUG_MODE.md',
    'docs/AUTO_UPDATE_USER_FLOW.md',
    'docs/DEVICE_REGISTRATION_DESIGN.md',
    'docs/CLI_HELP_OUTPUT_REFERENCE.md',
    
    # Current CLI summary
    'CLI_COMPLETE_SUMMARY.md',
}

def main():
    print("=" * 70)
    print("Documentation Cleanup - Keeping Only Essential Files")
    print("=" * 70)
    print()
    
    # Get all markdown files
    root_md = list(Path('.').glob('*.md'))
    docs_md = list(Path('docs').glob('*.md')) if Path('docs').exists() else []
    all_md = root_md + docs_md
    
    # Get all txt files (except requirements)
    txt_files = [
        f for f in Path('.').glob('*.txt') 
        if 'requirements' not in f.name.lower() and 'third-party' not in f.name.lower()
    ]
    
    removed_count = 0
    kept_count = 0
    
    # Process markdown files
    print("Processing markdown files...")
    for md_file in all_md:
        relative_path = str(md_file).replace('\\', '/')
        
        if relative_path in KEEP_DOCS or md_file.name in KEEP_DOCS:
            print(f"  ✅ KEEP: {md_file.name}")
            kept_count += 1
        else:
            try:
                md_file.unlink()
                print(f"  🗑️  Removed: {md_file.name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Error removing {md_file.name}: {e}")
    
    # Remove non-essential text files
    print("\nProcessing text files...")
    keep_txt = {'requirements.txt', 'chloros_cli_requirements.txt', 'START_HERE.txt', 'WHAT_TO_SIGN.txt'}
    
    for txt_file in txt_files:
        if txt_file.name in keep_txt:
            print(f"  ✅ KEEP: {txt_file.name}")
            kept_count += 1
        else:
            try:
                txt_file.unlink()
                print(f"  🗑️  Removed: {txt_file.name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Error removing {txt_file.name}: {e}")
    
    print()
    print("=" * 70)
    print(f"Summary:")
    print(f"  Removed: {removed_count} files")
    print(f"  Kept: {len(KEEP_DOCS)} essential files")
    print()
    print("✅ Documentation cleanup complete!")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()

