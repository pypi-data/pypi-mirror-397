#!/usr/bin/env python3
"""
Test what happens when Nuitka tries to import the compatibility fix.
"""
import sys
import os

print(f"[TEST] Python frozen: {getattr(sys, 'frozen', False)}")
print(f"[TEST] Current directory: {os.getcwd()}")
print(f"[TEST] Python path: {sys.path}")

try:
    print("[TEST] Attempting to import nuitka_ray_compatibility_fix...")
    from nuitka_ray_compatibility_fix import configure_ray_for_nuitka
    print("[TEST] ✅ Import successful!")
    
    config = configure_ray_for_nuitka()
    print(f"[TEST] ✅ Config: {config}")
    
except Exception as e:
    print(f"[TEST] ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

print("[TEST] Test complete.")
