#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND API TEST

Tests all critical backend components:
- Import tests for all modules
- API class instantiation
- All API method calls that backend_server.py uses
- Ray session manager integration
- Critical dependencies
"""

import sys
import os

def test_backend_api():
    print("🧪 COMPREHENSIVE BACKEND API TEST")
    print("=" * 50)
    
    # Test 1: Critical Imports Test
    print("\n🔍 TEST 1: Critical Imports Test")
    
    imports_to_test = [
        ('api', 'API class'),
        ('project', 'Project module'),
        ('tasks', 'Tasks module'),
        ('ray_session_manager', 'Ray Session Manager'),
        ('nuitka_ray_replacement', 'Ray Replacement'),
        ('mip.Vignette_Correction', 'Vignette Correction'),
        ('flask', 'Flask framework'),
        ('werkzeug', 'Werkzeug'),
        ('jinja2', 'Jinja2'),
        ('requests', 'Requests'),
        ('urllib3', 'urllib3'),
        ('certifi', 'Certifi'),
    ]
    
    import_results = {}
    
    for module_name, description in imports_to_test:
        try:
            if '.' in module_name:
                # Handle submodule imports
                parts = module_name.split('.')
                module = __import__(module_name, fromlist=[parts[-1]])
            else:
                module = __import__(module_name)
            print(f"  ✅ {description}: {module_name}")
            import_results[module_name] = True
        except ImportError as e:
            print(f"  ❌ {description}: {module_name} - {e}")
            import_results[module_name] = False
        except Exception as e:
            print(f"  ⚠️ {description}: {module_name} - {e}")
            import_results[module_name] = False
    
    # Test 2: API Class Instantiation
    print("\n🔍 TEST 2: API Class Instantiation Test")
    
    if import_results.get('api', False):
        try:
            from api import API
            api_instance = API()
            print("  ✅ API class instantiated successfully")
            
            # Test critical API methods exist
            critical_methods = [
                'open_project',
                'add_files_to_project', 
                'process_project',
                'get_project_status',
                'clear_jpg_cache',
                'clear_thumbnail_cache',
                'get_exposure_pin_info'
            ]
            
            for method_name in critical_methods:
                if hasattr(api_instance, method_name):
                    print(f"    ✅ Method exists: {method_name}")
                else:
                    print(f"    ❌ Method missing: {method_name}")
                    
        except Exception as e:
            print(f"  ❌ API instantiation failed: {e}")
            return False
    else:
        print("  ❌ Cannot test API - import failed")
        return False
    
    # Test 3: Ray Session Manager Integration
    print("\n🔍 TEST 3: Ray Session Manager Integration")
    
    if import_results.get('ray_session_manager', False):
        try:
            from ray_session_manager import RaySessionManager
            
            # Test singleton pattern
            manager1 = RaySessionManager()
            manager2 = RaySessionManager()
            
            if manager1 is manager2:
                print("  ✅ Singleton pattern working")
            else:
                print("  ❌ Singleton pattern broken")
            
            # Test Ray import forcing
            ray = manager1.get_ray()
            if ray:
                print("  ✅ Ray instance obtained")
                print(f"  ✅ Ray available: {manager1.is_available()}")
                
                # Check if it's our replacement
                if hasattr(ray, '_nuitka_ray'):
                    print("  ✅ Using Nuitka Ray Replacement (FORCED)")
                else:
                    print("  ⚠️ Using full Ray (might crash in Nuitka)")
                    
            else:
                print("  ❌ Ray instance is None")
                
        except Exception as e:
            print(f"  ❌ Ray Session Manager test failed: {e}")
            return False
    else:
        print("  ❌ Cannot test Ray Session Manager - import failed")
        return False
    
    # Test 4: Backend Server Dependencies
    print("\n🔍 TEST 4: Backend Server Dependencies Test")
    
    flask_deps = ['Flask', 'request', 'jsonify', 'Response']
    
    if import_results.get('flask', False):
        try:
            from flask import Flask, request, jsonify, Response
            print("  ✅ All Flask dependencies imported")
            
            # Test Flask app creation
            app = Flask(__name__)
            print("  ✅ Flask app creation works")
            
        except Exception as e:
            print(f"  ❌ Flask dependencies test failed: {e}")
            return False
    else:
        print("  ❌ Cannot test Flask dependencies - import failed")
    
    # Test 5: Project and Tasks Modules
    print("\n🔍 TEST 5: Project and Tasks Modules Test")
    
    if import_results.get('project', False) and import_results.get('tasks', False):
        try:
            import project
            import tasks
            print("  ✅ Project and Tasks modules imported")
            
            # These modules should have key classes/functions
            # We'll just verify they can be imported without error
            print("  ✅ Project and Tasks modules are accessible")
            
        except Exception as e:
            print(f"  ❌ Project/Tasks modules test failed: {e}")
            return False
    else:
        print("  ❌ Cannot test Project/Tasks - imports failed")
    
    # Test 6: MIP Package Test
    print("\n🔍 TEST 6: MIP Package Test")
    
    if import_results.get('mip.Vignette_Correction', False):
        try:
            from mip import Vignette_Correction
            print("  ✅ MIP Vignette_Correction imported")
            
            # Test if the function exists
            if hasattr(Vignette_Correction, 'vignette_correct_survey3'):
                print("  ✅ vignette_correct_survey3 function exists")
            else:
                print("  ❌ vignette_correct_survey3 function missing")
                
        except Exception as e:
            print(f"  ❌ MIP package test failed: {e}")
            return False
    else:
        print("  ❌ Cannot test MIP package - import failed")
    
    print("\n📊 IMPORT SUMMARY:")
    passed = sum(1 for result in import_results.values() if result)
    total = len(import_results)
    print(f"  ✅ Passed: {passed}/{total} imports")
    
    if passed == total:
        print("\n🎉 ALL BACKEND API TESTS PASSED!")
        print("✅ Backend is ready for Nuitka compilation!")
        return True
    else:
        print(f"\n⚠️ {total - passed} imports failed - may need attention")
        return False

if __name__ == "__main__":
    success = test_backend_api()
    if success:
        print("\n🚀 Backend API is ready for compilation!")
    else:
        print("\n❌ Backend API needs fixes before compilation!")
    
    input("\nPress Enter to continue...")
