#!/usr/bin/env python3
"""
Test if we can import the compatibility fix in a Nuitka executable.
"""
import sys
import os

print(f"[TEST] 🧪 Testing Nuitka compatibility fix import...")
print(f"[TEST] Python frozen: {getattr(sys, 'frozen', False)}")
print(f"[TEST] Current directory: {os.getcwd()}")

try:
    print("[TEST] 1. Importing nuitka_ray_compatibility_fix...")
    from nuitka_ray_compatibility_fix import configure_ray_for_nuitka
    print("[TEST] ✅ Import successful!")
    
    print("[TEST] 2. Configuring Ray...")
    config = configure_ray_for_nuitka()
    print(f"[TEST] ✅ Config: {config}")
    
    print("[TEST] 3. Testing Ray import...")
    import ray
    print("[TEST] ✅ Ray imported successfully!")
    
    print("[TEST] 🎉 ALL TESTS PASSED!")
    
except Exception as e:
    print(f"[TEST] ❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

input("Press Enter to exit...")
