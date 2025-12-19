"""
Quick test of rebuilt SDK and backend
"""
import time
import sys

print("="*70)
print("TESTING REBUILT SDK AND BACKEND")
print("="*70)

# Test 1: Import SDK
print("\n1. Testing SDK import...")
try:
    from chloros_sdk import ChlorosLocal
    print("   ✅ SDK imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Test 2: Connect to backend
print("\n2. Testing backend connection...")
try:
    chloros = ChlorosLocal(auto_start_backend=True, backend_startup_timeout=90)
    print("   ✅ Connected to backend")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Test 3: Check backend status
print("\n3. Checking backend status...")
try:
    status = chloros.get_status()
    if status.get('running'):
        print(f"   ✅ Backend is running: {status}")
    else:
        print(f"   ⚠️  Backend status unclear: {status}")
except Exception as e:
    print(f"   ❌ Status check failed: {e}")

# Test 4: THE CRITICAL TEST - Create project (this was broken before)
print("\n4. Testing project creation (THE BUG FIX TEST)...")
try:
    project_name = f"BugFixTest_{int(time.time())}"
    result = chloros.create_project(project_name, camera="Survey3N_RGN")
    print(f"   ✅ PROJECT CREATION WORKS! Result: {result}")
    print("   ✅✅✅ BUG FIX CONFIRMED - PROJECT CREATION SUCCESSFUL! ✅✅✅")
except Exception as e:
    print(f"   ❌ PROJECT CREATION FAILED: {e}")
    print("   ❌❌❌ BUG STILL EXISTS OR NEW ISSUE! ❌❌❌")
    chloros.shutdown_backend()
    sys.exit(1)

# Test 5: Import validation
print("\n5. Testing import validation...")
try:
    chloros.import_images("C:/NonExistent/Folder")
    print("   ❌ Should have raised error")
except FileNotFoundError:
    print("   ✅ Input validation works correctly")
except Exception as e:
    print(f"   ⚠️  Unexpected error: {e}")

# Test 6: Configure
print("\n6. Testing configuration...")
try:
    result = chloros.configure(
        vignette_correction=True,
        reflectance_calibration=True,
        indices=["NDVI", "NDRE"]
    )
    print(f"   ✅ Configuration works: {result}")
except Exception as e:
    print(f"   ❌ Configuration failed: {e}")

# Test 7: Get config
print("\n7. Testing get_config...")
try:
    config = chloros.get_config()
    print(f"   ✅ Get config works, keys: {list(config.keys())}")
except Exception as e:
    print(f"   ❌ Get config failed: {e}")

# Cleanup
print("\n8. Cleaning up...")
try:
    chloros.shutdown_backend()
    print("   ✅ Backend shutdown")
except Exception as e:
    print(f"   ⚠️  Shutdown warning: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)
print("\nKey Result: PROJECT CREATION BUG FIX ✅ VERIFIED")
print("\nThe rebuilt backend correctly handles project creation!")
print("="*70 + "\n")









