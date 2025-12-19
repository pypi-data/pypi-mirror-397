"""
Manual SDK Test Script
======================

This script performs real-world testing of the Chloros SDK.
It tests actual API calls against the Chloros backend.

Requirements:
- Chloros backend must be running (or SDK will auto-start it)
- Active Chloros+ license (logged in via GUI)

Usage:
    python test_sdk_manual.py
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Import SDK
try:
    from chloros_sdk import ChlorosLocal, process_folder
    from chloros_sdk.exceptions import (
        ChlorosError,
        ChlorosBackendError,
        ChlorosConnectionError,
        ChlorosProcessingError
    )
    print("✅ SDK imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SDK: {e}")
    sys.exit(1)


def test_version():
    """Test SDK version is accessible"""
    try:
        import chloros_sdk
        version = chloros_sdk.__version__
        print(f"✅ SDK Version: {version}")
        return True
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False


def test_initialization():
    """Test SDK initialization"""
    try:
        # Try with auto_start_backend=False first to see if backend is running
        try:
            chloros = ChlorosLocal(auto_start_backend=False)
            print("✅ Connected to running backend")
            chloros.shutdown_backend()
            return True
        except ChlorosConnectionError:
            print("ℹ️  Backend not running, testing auto-start...")
            # Try with auto-start
            try:
                chloros = ChlorosLocal(auto_start_backend=True)
                print("✅ Backend auto-started successfully")
                chloros.shutdown_backend()
                return True
            except Exception as e:
                print(f"❌ Failed to auto-start backend: {e}")
                return False
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        return False


def test_context_manager():
    """Test context manager functionality"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            status = chloros.get_status()
            print(f"✅ Context manager works, backend running: {status['running']}")
        print("✅ Context manager cleanup successful")
        return True
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False


def test_get_status():
    """Test get_status method"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            status = chloros.get_status()
            if status.get('running'):
                print(f"✅ get_status() returned: {status}")
                return True
            else:
                print(f"⚠️  Backend status unclear: {status}")
                return False
    except Exception as e:
        print(f"❌ get_status test failed: {e}")
        return False


def test_create_project():
    """Test project creation"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            # Create a test project with a unique name
            import time
            project_name = f"SDK_Test_{int(time.time())}"
            
            try:
                result = chloros.create_project(project_name)
                print(f"✅ Project created: {result}")
                return True
            except ChlorosProcessingError as e:
                # Check if it's a known issue
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    print(f"⚠️  Project name collision: {error_msg}")
                    return True  # This is acceptable
                else:
                    print(f"❌ Project creation failed: {e}")
                    return False
    except Exception as e:
        print(f"❌ create_project test failed: {e}")
        return False


def test_import_images_validation():
    """Test import_images input validation"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            # Test non-existent folder
            try:
                chloros.import_images("C:/NonExistent/Folder")
                print("❌ Should have raised FileNotFoundError")
                return False
            except FileNotFoundError:
                print("✅ Correctly raised FileNotFoundError for non-existent folder")
                return True
    except Exception as e:
        print(f"❌ import_images validation test failed: {e}")
        return False


def test_configure():
    """Test configuration method"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            # Create a test project first
            import time
            project_name = f"SDK_Config_Test_{int(time.time())}"
            chloros.create_project(project_name)
            
            # Test configuration
            result = chloros.configure(
                vignette_correction=True,
                reflectance_calibration=True,
                indices=["NDVI", "NDRE"]
            )
            print(f"✅ Configuration set successfully: {result}")
            return True
    except Exception as e:
        print(f"❌ configure test failed: {e}")
        return False


def test_get_config():
    """Test get_config method"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            config = chloros.get_config()
            print(f"✅ get_config() returned config with keys: {list(config.keys())}")
            return True
    except Exception as e:
        print(f"❌ get_config test failed: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    try:
        # Test that helpful error is raised when trying to import non-existent folder
        # (We can't test backend connection without actually stopping the backend)
        with ChlorosLocal(auto_start_backend=False) as chloros:
            try:
                # Create temp file (not directory)
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
                    temp_file = f.name
                    f.write(b"test")
                
                # Try to import it as a folder - should fail
                try:
                    chloros.import_images(temp_file)
                    print("❌ Should have raised ValueError for file instead of folder")
                    return False
                except ValueError as e:
                    if "not a directory" in str(e).lower():
                        print(f"✅ Correctly raised error: {type(e).__name__}: {e}")
                        return True
                    else:
                        print(f"❌ Wrong error message: {e}")
                        return False
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            except Exception as e:
                print(f"❌ Error test failed: {e}")
                return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_path_handling():
    """Test Path object handling"""
    try:
        with ChlorosLocal(auto_start_backend=False) as chloros:
            # Test with Path object
            test_path = Path("C:/NonExistent/Folder")
            try:
                chloros.import_images(test_path)
                print("❌ Should have raised FileNotFoundError")
                return False
            except FileNotFoundError:
                print("✅ Path objects are handled correctly")
                return True
    except Exception as e:
        print(f"❌ Path handling test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("CHLOROS SDK COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        ("Version Check", test_version),
        ("Initialization", test_initialization),
        ("Context Manager", test_context_manager),
        ("Get Status", test_get_status),
        ("Create Project", test_create_project),
        ("Import Images Validation", test_import_images_validation),
        ("Configure", test_configure),
        ("Get Config", test_get_config),
        ("Error Handling", test_error_handling),
        ("Path Handling", test_path_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- Testing: {test_name} ---")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! SDK is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

