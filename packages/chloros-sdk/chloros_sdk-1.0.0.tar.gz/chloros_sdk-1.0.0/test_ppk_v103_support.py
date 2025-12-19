#!/usr/bin/env python3
"""
Test script for PPK v1.03 auto-calibration support.

This script verifies that the new PPK detection and processing functions work correctly.
"""

import sys
import os

# Add the parent directory to the path so we can import mip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary functions can be imported"""
    print("=" * 70)
    print("TEST 1: Import Functions")
    print("=" * 70)
    
    try:
        from mip.ppk import (
            detect_ppk_method,
            analyze_auto_calibration_quality,
            load_ppk_data,
            lerp_pulse_coords,
            apply_ppk_corrections
        )
        print("✅ All PPK functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_detect_ppk_method():
    """Test the PPK method detection function"""
    print("\n" + "=" * 70)
    print("TEST 2: PPK Method Detection")
    print("=" * 70)
    
    from mip.ppk import detect_ppk_method
    
    # Test with non-existent file (should return 'legacy' gracefully)
    print("\nTest 2a: Non-existent file")
    method = detect_ppk_method("nonexistent.daq")
    print(f"Result: {method}")
    assert method == 'legacy', "Should return 'legacy' for non-existent files"
    print("✅ Gracefully handles non-existent files")
    
    return True


def test_sql_queries():
    """Test that SQL queries are defined correctly"""
    print("\n" + "=" * 70)
    print("TEST 3: SQL Query Definitions")
    print("=" * 70)
    
    from mip import ppk
    
    # Check that both SQL queries exist
    assert hasattr(ppk, 'SQL_get_ppk_data'), "Legacy SQL query not found"
    assert hasattr(ppk, 'SQL_get_ppk_data_v103'), "v1.03 SQL query not found"
    
    print("\n✅ SQL_get_ppk_data (legacy) defined:")
    print(ppk.SQL_get_ppk_data.strip())
    
    print("\n✅ SQL_get_ppk_data_v103 (new) defined:")
    print(ppk.SQL_get_ppk_data_v103.strip())
    
    # Verify new query includes auto-calibration columns
    assert 'precise_timestamp' in ppk.SQL_get_ppk_data_v103
    assert 'auto_cal_offset' in ppk.SQL_get_ppk_data_v103
    assert 'auto_cal_confidence' in ppk.SQL_get_ppk_data_v103
    assert 'auto_cal_applied' in ppk.SQL_get_ppk_data_v103
    assert 'auto_cal_system_sig' in ppk.SQL_get_ppk_data_v103
    
    print("\n✅ v1.03 query includes all required auto-calibration columns")
    
    return True


def test_analyze_auto_calibration_quality():
    """Test the auto-calibration quality analysis function"""
    print("\n" + "=" * 70)
    print("TEST 4: Auto-Calibration Quality Analysis")
    print("=" * 70)
    
    from mip.ppk import analyze_auto_calibration_quality
    
    # Test with non-existent file (should return empty dict gracefully)
    print("\nTest 4a: Non-existent file")
    quality = analyze_auto_calibration_quality("nonexistent.daq")
    print(f"Result: {quality}")
    assert quality == {}, "Should return empty dict for non-existent files"
    print("✅ Gracefully handles non-existent files")
    
    return True


def test_backward_compatibility():
    """Verify backward compatibility features"""
    print("\n" + "=" * 70)
    print("TEST 5: Backward Compatibility")
    print("=" * 70)
    
    from mip.ppk import lerp_pulse_coords, load_ppk_data
    import inspect
    
    # Check lerp_pulse_coords has ppk_method parameter with default
    sig = inspect.signature(lerp_pulse_coords)
    assert 'ppk_method' in sig.parameters, "lerp_pulse_coords missing ppk_method parameter"
    assert sig.parameters['ppk_method'].default == 'legacy', "Default should be 'legacy'"
    print("✅ lerp_pulse_coords defaults to legacy method")
    
    # Check load_ppk_data returns tuple
    sig = inspect.signature(load_ppk_data)
    print(f"✅ load_ppk_data signature: {sig}")
    
    return True


def test_documentation():
    """Verify documentation file was created"""
    print("\n" + "=" * 70)
    print("TEST 6: Documentation")
    print("=" * 70)
    
    doc_path = "PPK_V103_SUPPORT.md"
    if os.path.exists(doc_path):
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        assert 'v1.03' in content, "Documentation should mention v1.03"
        assert 'auto-calibration' in content.lower(), "Documentation should mention auto-calibration"
        assert 'legacy' in content.lower(), "Documentation should mention legacy support"
        
        print(f"✅ Documentation file exists: {doc_path}")
        print(f"   Size: {len(content)} bytes")
        print(f"   Lines: {content.count(chr(10)) + 1}")
        return True
    else:
        print(f"⚠️  Documentation file not found: {doc_path}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "PPK v1.03 Support Test Suite" + " " * 25 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Import Functions", test_imports),
        ("PPK Method Detection", test_detect_ppk_method),
        ("SQL Query Definitions", test_sql_queries),
        ("Auto-Calibration Quality Analysis", test_analyze_auto_calibration_quality),
        ("Backward Compatibility", test_backward_compatibility),
        ("Documentation", test_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! PPK v1.03 support is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

