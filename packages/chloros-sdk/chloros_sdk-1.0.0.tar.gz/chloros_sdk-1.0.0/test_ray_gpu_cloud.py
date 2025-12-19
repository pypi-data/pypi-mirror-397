#!/usr/bin/env python3
"""Test Ray and GPU configuration before rebuilding the backend."""

import sys
import os

print("=" * 60)
print("RAY AND GPU CLOUD COMPATIBILITY TEST")
print("=" * 60)

print(f"\nPython: {sys.version}")
print(f"Frozen: {getattr(sys, 'frozen', False)}")
print(f"Platform: {sys.platform}")

# Test Ray import
print("\n" + "=" * 40)
print("TESTING RAY")
print("=" * 40)

try:
    import ray
    print(f"✅ Ray imported successfully")
    print(f"   Version: {ray.__version__}")
    
    # Test Ray initialization with local mode (same as cloud/Nuitka)
    configs_to_test = [
        {
            'name': 'Cloud mode (local_mode=True)',
            'config': {
                'local_mode': True,
                'num_cpus': 4,
                'num_gpus': 0,
                'include_dashboard': False,
                'ignore_reinit_error': True,
                'log_to_driver': False,
                'logging_level': 'error',
            }
        },
        {
            'name': 'Minimal config',
            'config': {
                'local_mode': True,
                'num_cpus': 1,
                'num_gpus': 0,
                'include_dashboard': False,
                'ignore_reinit_error': True,
            }
        },
    ]
    
    for test in configs_to_test:
        print(f"\n   Testing: {test['name']}")
        print(f"   Config: {test['config']}")
        try:
            ray.shutdown()
        except:
            pass
        
        try:
            ray.init(**test['config'])
            print(f"   ✅ Ray initialized: {ray.is_initialized()}")
            print(f"   Resources: {ray.available_resources()}")
            ray.shutdown()
            print(f"   ✅ Ray shutdown OK")
        except Exception as e:
            print(f"   ❌ Ray init failed: {e}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"❌ Ray import failed: {e}")
except Exception as e:
    print(f"❌ Ray error: {e}")
    import traceback
    traceback.print_exc()

# Test GPU/CUDA
print("\n" + "=" * 40)
print("TESTING GPU/CUDA")
print("=" * 40)

try:
    import torch
    print(f"✅ PyTorch imported successfully")
    print(f"   Version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"   CUDA device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"   Device {i}: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"      Memory: {props.total_memory / 1024**3:.1f} GB")
    else:
        print("   ⚠️ No CUDA devices available")
        
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")
except Exception as e:
    print(f"❌ PyTorch/CUDA error: {e}")
    import traceback
    traceback.print_exc()

# Test the actual ray_session_manager
print("\n" + "=" * 40)
print("TESTING RAY_SESSION_MANAGER")
print("=" * 40)

try:
    # Add the current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from ray_session_manager import get_ray_session, RaySessionManager
    
    print("✅ ray_session_manager imported successfully")
    
    session = get_ray_session()
    print(f"   Session instance: {session}")
    print(f"   Is available: {session.is_available()}")
    
    # Test initialization
    print("\n   Testing session initialization...")
    result = session.initialize_session(mode='premium', max_workers=4)
    print(f"   Initialize result: {result}")
    
    if result:
        ray_instance = session.get_initialized_ray('premium')
        if ray_instance:
            print(f"   ✅ Got initialized Ray: {ray_instance.is_initialized()}")
        else:
            print("   ❌ get_initialized_ray returned None")
    
    session.shutdown()
    print("   ✅ Session shutdown OK")
    
except Exception as e:
    print(f"❌ ray_session_manager error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)




