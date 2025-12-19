"""Test critical functionality for Nuitka frozen exe"""
import sys
import os

print("=" * 60)
print("NUITKA COMPATIBILITY TEST")
print("=" * 60)

errors = []
warnings = []

# Test 1: Ray and msgpack
print("\n[TEST 1] Ray dependencies...")
try:
    import msgpack
    print("  PASS: msgpack version:", msgpack.version)
except ImportError as e:
    errors.append(f"msgpack import failed: {e}")
    print("  FAIL: msgpack not available")

try:
    import ray
    print("  PASS: Ray version:", ray.__version__)
except ImportError as e:
    errors.append(f"Ray import failed: {e}")
    print("  FAIL: Ray not available")

# Test 2: Vignette correction (the bug we just fixed)
print("\n[TEST 2] Vignette correction...")
try:
    sys.path.insert(0, '.')
    from mip.Vignette_Correction import ApplyVig
    print("  PASS: Vignette correction imports without error")
    
    # Check for the 'import os' bug
    import inspect
    source = inspect.getsource(ApplyVig)
    if '    import os' in source and source.count('import os') > 1:
        errors.append("Vignette_Correction.py still has redundant 'import os' inside function!")
        print("  FAIL: Redundant 'import os' found in function")
    else:
        print("  PASS: No redundant 'import os' in function")
except Exception as e:
    errors.append(f"Vignette correction test failed: {e}")
    print(f"  FAIL: {e}")

# Test 3: Compilation detection
print("\n[TEST 3] Compilation detection logic...")
try:
    from mip.ExifUtils import ExifUtils
    from mip.Save_Format import configpath as save_format_config
    from mip.ConvertSurvey3ToTiff import configpath as convert_config
    print("  PASS: All modules with compilation detection imported")
    
    # Verify they all use the correct detection
    modules_to_check = [
        'mip/ExifUtils.py',
        'mip/Vignette_Correction.py', 
        'mip/Save_Format.py',
        'mip/ConvertSurvey3ToTiff.py'
    ]
    
    for module in modules_to_check:
        if os.path.exists(module):
            with open(module, 'r', encoding='utf-8') as f:
                content = f.read()
                if "getattr(sys, 'frozen', False) or '__compiled__' in globals()" in content:
                    print(f"  PASS: {module} has correct Nuitka detection")
                else:
                    warnings.append(f"{module} may not detect Nuitka correctly")
                    print(f"  WARN: {module} may not detect Nuitka correctly")
except Exception as e:
    errors.append(f"Compilation detection test failed: {e}")
    print(f"  FAIL: {e}")

# Test 4: Resource file paths
print("\n[TEST 4] Resource files...")
required_files = [
    'exiftool.exe',
    'pix4d.config',
    'mapir.config',
    'flatFields/S3W/Average Flat Field Correction ImageB.tif',
    'flatFields/S3W/Average Flat Field Correction ImageG.tif',
    'flatFields/S3W/Average Flat Field Correction ImageR.tif',
]

for file in required_files:
    if os.path.exists(file):
        print(f"  PASS: {file}")
    else:
        warnings.append(f"Resource file missing: {file}")
        print(f"  WARN: {file} not found (needed for Nuitka build)")

# Test 5: GPU module (optional)
print("\n[TEST 5] GPU acceleration (optional)...")
try:
    from gpu_image_ops import is_gpu_available, gpu_health_check
    print("  PASS: GPU module imported")
    
    avail = is_gpu_available()
    print(f"  INFO: GPU available: {avail}")
    
    if avail:
        healthy, msg = gpu_health_check()
        print(f"  INFO: GPU health: {healthy} - {msg}")
except ImportError:
    print("  INFO: GPU module not available (will use CPU - OK)")
except Exception as e:
    warnings.append(f"GPU test error: {e}")
    print(f"  WARN: GPU test error: {e}")

# Test 6: Ray initialization test
print("\n[TEST 6] Ray initialization...")
try:
    import ray
    ray.init(ignore_reinit_error=True, log_to_driver=False, num_cpus=2, num_gpus=0)
    print("  PASS: Ray initialized")
    
    @ray.remote
    def test_func(x):
        return x * 2
    
    result = ray.get(test_func.remote(21))
    if result == 42:
        print("  PASS: Ray remote function works")
    else:
        errors.append("Ray remote function returned wrong result")
        print(f"  FAIL: Expected 42, got {result}")
    
    ray.shutdown()
    print("  PASS: Ray shutdown clean")
except Exception as e:
    errors.append(f"Ray initialization failed: {e}")
    print(f"  FAIL: {e}")

# Test 7: Check for other potential import issues
print("\n[TEST 7] Core processing functions...")
try:
    from tasks import detect_calibration_image, process_image_unified
    print("  PASS: Core processing functions import")
except Exception as e:
    errors.append(f"Core functions import failed: {e}")
    print(f"  FAIL: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\nCRITICAL ERRORS (must fix before rebuilding):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

if warnings:
    print("\nWARNINGS (should fix before rebuilding):")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")

if not errors and not warnings:
    print("\nALL TESTS PASSED! Safe to rebuild.")
    sys.exit(0)
elif not errors:
    print("\nNo critical errors. Warnings can be addressed but rebuild should work.")
    sys.exit(0)
else:
    print("\nCRITICAL ERRORS FOUND! Fix these before rebuilding.")
    sys.exit(1)

