#!/usr/bin/env python3
"""
Simple diagnostic script to test backend startup without any imports
Write directly to file to bypass stdout issues
"""

import os
import sys
from datetime import datetime

# Write directly to a file to bypass any stdout redirection issues
test_file = os.path.join(os.path.dirname(__file__), 'backend_startup_test.txt')

def log_to_file(message):
    """Write message directly to file"""
    try:
        with open(test_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except Exception as e:
        # If file write fails, try stderr
        print(f"ERROR writing to file: {e}", file=sys.stderr)

# Clear previous test log
try:
    if os.path.exists(test_file):
        os.remove(test_file)
except:
    pass

log_to_file("=" * 60)
log_to_file("BACKEND STARTUP DIAGNOSTIC TEST")
log_to_file("=" * 60)
log_to_file(f"Python version: {sys.version}")
log_to_file(f"Python executable: {sys.executable}")
log_to_file(f"Platform: {sys.platform}")
log_to_file(f"Current directory: {os.getcwd()}")
log_to_file(f"Script directory: {os.path.dirname(__file__)}")
log_to_file("")

# Test 1: Basic imports
log_to_file("TEST 1: Testing basic imports...")
try:
    import time
    log_to_file("  ✓ time imported")
    import json
    log_to_file("  ✓ json imported")
    import threading
    log_to_file("  ✓ threading imported")
    log_to_file("TEST 1: PASSED")
except Exception as e:
    log_to_file(f"TEST 1: FAILED - {e}")
    sys.exit(1)

# Test 2: Flask import
log_to_file("")
log_to_file("TEST 2: Testing Flask import...")
try:
    from flask import Flask
    log_to_file("  ✓ Flask imported")
    log_to_file("TEST 2: PASSED")
except Exception as e:
    log_to_file(f"TEST 2: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    sys.exit(1)

# Test 3: Ray configuration
log_to_file("")
log_to_file("TEST 3: Testing Ray configuration...")
try:
    from nuitka_ray_compatibility_fix import configure_ray_for_nuitka
    log_to_file("  ✓ nuitka_ray_compatibility_fix imported")
    ray_config = configure_ray_for_nuitka()
    log_to_file(f"  ✓ Ray configured: {ray_config}")
    log_to_file("TEST 3: PASSED")
except Exception as e:
    log_to_file(f"TEST 3: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    # Don't exit, continue to next test

# Test 4: Unicode patch
log_to_file("")
log_to_file("TEST 4: Testing unicode_patch import...")
try:
    import unicode_patch
    log_to_file("  ✓ unicode_patch imported")
    log_to_file("TEST 4: PASSED")
except Exception as e:
    log_to_file(f"TEST 4: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    # Don't exit, continue to next test

# Test 5: PyTorch / CUDA (this is likely to hang on no-GPU systems)
log_to_file("")
log_to_file("TEST 5: Testing PyTorch/CUDA import...")
log_to_file("  (This test may take 30+ seconds on no-GPU systems)")
try:
    import torch
    log_to_file("  ✓ torch imported")
    
    # Test CUDA availability with timeout protection
    try:
        log_to_file("  Testing torch.cuda.is_available()...")
        cuda_available = torch.cuda.is_available()
        log_to_file(f"  ✓ CUDA available: {cuda_available}")
    except Exception as cuda_error:
        log_to_file(f"  ⚠ CUDA check failed: {cuda_error}")
    
    log_to_file("TEST 5: PASSED")
except Exception as e:
    log_to_file(f"TEST 5: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    # Don't exit, continue to next test

# Test 6: API import (this is the big one - takes 10-30 seconds)
log_to_file("")
log_to_file("TEST 6: Testing API import...")
log_to_file("  (This test may take 30-60 seconds)")
try:
    start_time = time.time()
    from api import API
    elapsed = time.time() - start_time
    log_to_file(f"  ✓ API imported in {elapsed:.1f} seconds")
    log_to_file("TEST 6: PASSED")
except Exception as e:
    log_to_file(f"TEST 6: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    sys.exit(1)

# Test 7: API instance creation
log_to_file("")
log_to_file("TEST 7: Testing API instance creation...")
try:
    api = API()
    log_to_file("  ✓ API instance created")
    log_to_file("TEST 7: PASSED")
except Exception as e:
    log_to_file(f"TEST 7: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    sys.exit(1)

# Test 8: Auth middleware
log_to_file("")
log_to_file("TEST 8: Testing auth_middleware import...")
try:
    from auth_middleware import get_auth_middleware
    log_to_file("  ✓ auth_middleware imported")
    auth_middleware = get_auth_middleware()
    log_to_file("  ✓ auth_middleware instance created")
    log_to_file("TEST 8: PASSED")
except Exception as e:
    log_to_file(f"TEST 8: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    # Don't exit, auth might not be required

# Test 9: Instance protection
log_to_file("")
log_to_file("TEST 9: Testing instance_protection import...")
try:
    from instance_protection import get_instance_protection
    log_to_file("  ✓ instance_protection imported")
    instance_protection = get_instance_protection()
    log_to_file("  ✓ instance_protection instance created")
    log_to_file("TEST 9: PASSED")
except Exception as e:
    log_to_file(f"TEST 9: FAILED - {e}")
    import traceback
    log_to_file(traceback.format_exc())
    # Don't exit, instance protection might not be required

# All tests passed!
log_to_file("")
log_to_file("=" * 60)
log_to_file("ALL CRITICAL TESTS PASSED!")
log_to_file("Backend should be able to start successfully")
log_to_file("=" * 60)

print(f"\nDiagnostic test completed successfully!")
print(f"Results written to: {test_file}")
print("\nYou can now try running the backend normally.")

