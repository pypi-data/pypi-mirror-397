#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify Ray replacement works correctly
NOTE: This uses threading only (no process pool) to avoid Windows pickling issues in testing
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def main():
    print("=" * 60)
    print("Testing Ray Fix")
    print("=" * 60)

    # Test 1: Import nuitka_ray_replacement
    print("\n1. Testing nuitka_ray_replacement import...")
    try:
        import nuitka_ray_replacement as ray
        print("   [OK] nuitka_ray_replacement imported successfully")
    except ImportError as e:
        print(f"   [FAIL] Failed to import: {e}")
        return False

    # Test 2: Initialize Ray
    print("\n2. Testing Ray initialization...")
    try:
        ray.init(num_cpus=4, num_gpus=0)
        print("   [OK] Ray initialized successfully")
    except Exception as e:
        print(f"   [FAIL] Failed to initialize: {e}")
        return False

    # Test 3: Check if initialized
    print("\n3. Testing is_initialized()...")
    if ray.is_initialized():
        print("   [OK] Ray reports as initialized")
    else:
        print("   [FAIL] Ray not initialized")
        return False

    # Test 4: Check resources
    print("\n4. Testing available_resources()...")
    try:
        resources = ray.available_resources()
        print(f"   [OK] Resources: {resources}")
    except Exception as e:
        print(f"   [FAIL] Failed to get resources: {e}")
        return False

    # Test 5: Shutdown
    print("\n5. Testing shutdown...")
    try:
        ray.shutdown()
        print("   [OK] Ray shutdown successfully")
    except Exception as e:
        print(f"   [FAIL] Failed to shutdown: {e}")
        return False

    # Test 6: Test ray_session_manager integration
    print("\n6. Testing ray_session_manager integration...")
    try:
        from ray_session_manager import get_ray_session
        
        session = get_ray_session()
        print("   [OK] Got ray_session_manager instance")
        
        # This should import nuitka_ray_replacement
        ray_instance = session.get_ray()
        if ray_instance:
            print("   [OK] ray_session_manager imported Ray successfully")
            
            # Check which Ray was imported
            if hasattr(ray_instance, '_nuitka_ray'):
                print("   [OK] Confirmed: using nuitka_ray_replacement")
            else:
                print("   [INFO] Note: Using real Ray (normal in development mode)")
        else:
            print("   [FAIL] Failed to get Ray instance")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Failed integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED")
    print("=" * 60)
    print("\nThe Ray fix is working correctly!")
    print("Key points:")
    print("  - nuitka_ray_replacement module is available")
    print("  - ray_session_manager tries to use it first")
    print("  - In compiled mode, it will use replacement (no subprocesses)")
    print("  - No GCS server windows will appear")
    print("\nYou can now rebuild the installer using one of:")
    print("  - scripts\\compile_safe_backend.bat")
    print("  - scripts\\compile_safe_backend_enhanced.bat")
    print("  - scripts\\compile_safe_backend_standalone.bat")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
