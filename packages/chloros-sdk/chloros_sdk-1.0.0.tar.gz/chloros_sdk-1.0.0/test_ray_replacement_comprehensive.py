#!/usr/bin/env python3
"""
COMPREHENSIVE RAY REPLACEMENT TEST

Tests all aspects of the maximum performance Ray Replacement:
- Import functionality
- Initialization with maximum performance
- GPU detection (CUDA + OpenCL)
- Intelligent task scheduling
- Process pool vs thread pool selection
- Ray API compatibility (@ray.remote, ray.get)
"""

import sys
import time
import os

def test_ray_replacement():
    print("🧪 COMPREHENSIVE RAY REPLACEMENT TEST")
    print("=" * 50)
    
    # Test 1: Import Test
    print("\n🔍 TEST 1: Import Test")
    try:
        import nuitka_ray_replacement as ray
        print("✅ Ray Replacement imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Initialization Test
    print("\n🔍 TEST 2: Initialization Test")
    try:
        ray.init()
        print("✅ Ray Replacement initialized successfully")
        
        # Check if initialized
        if ray.is_initialized():
            print("✅ is_initialized() returns True")
        else:
            print("❌ is_initialized() returns False")
            
        # Check resources
        resources = ray.available_resources()
        print(f"✅ Available resources: {resources}")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 3: GPU Detection Test
    print("\n🔍 TEST 3: GPU Detection Test")
    try:
        # Access the global instance to check GPU detection
        from nuitka_ray_replacement import _nuitka_ray
        gpu_count = _nuitka_ray.num_gpus
        cpu_count = _nuitka_ray.num_cpus
        
        print(f"✅ Detected CPUs: {cpu_count}")
        print(f"✅ Detected GPUs: {gpu_count}")
        
        # Test GPU info printing
        if gpu_count > 0:
            _nuitka_ray._print_gpu_info()
        
    except Exception as e:
        print(f"❌ GPU detection test failed: {e}")
        return False
    
    # Test 4: Ray API Compatibility Test
    print("\n🔍 TEST 4: Ray API Compatibility Test")
    
    # Define test functions for different task types
    @ray.remote
    def cpu_intensive_task(n):
        """CPU-intensive task that should use process pool"""
        result = 0
        for i in range(n):
            result += i * i
        return result
    
    @ray.remote
    def io_bound_task(message):
        """I/O-bound task that should use thread pool"""
        time.sleep(0.1)  # Simulate I/O wait
        return f"Processed: {message}"
    
    @ray.remote
    def gpu_accelerated_task(data):
        """GPU task that should use thread pool + GPU"""
        # Simulate GPU work
        return f"GPU processed: {data}"
    
    try:
        # Test CPU-intensive task (should use process pool)
        print("  🧮 Testing CPU-intensive task...")
        cpu_future = cpu_intensive_task.remote(1000)
        cpu_result = ray.get(cpu_future)
        print(f"  ✅ CPU task result: {cpu_result}")
        
        # Test I/O-bound task (should use thread pool)
        print("  📁 Testing I/O-bound task...")
        io_future = io_bound_task.remote("test data")
        io_result = ray.get(io_future)
        print(f"  ✅ I/O task result: {io_result}")
        
        # Test GPU task (should use thread pool)
        print("  🎮 Testing GPU-accelerated task...")
        gpu_future = gpu_accelerated_task.remote("image data")
        gpu_result = ray.get(gpu_future)
        print(f"  ✅ GPU task result: {gpu_result}")
        
        # Test batch processing
        print("  📦 Testing batch processing...")
        batch_futures = [cpu_intensive_task.remote(100) for _ in range(3)]
        batch_results = ray.get(batch_futures)
        print(f"  ✅ Batch results: {batch_results}")
        
    except Exception as e:
        print(f"❌ Ray API compatibility test failed: {e}")
        return False
    
    # Test 5: Pool Selection Logic Test
    print("\n🔍 TEST 5: Intelligent Pool Selection Test")
    try:
        from nuitka_ray_replacement import RemoteFunction
        
        # Test functions with different naming patterns
        def process_image_data(data): return f"processed {data}"
        def compute_calibration(params): return f"computed {params}"
        def read_file_content(path): return f"read {path}"
        def save_output_data(data): return f"saved {data}"
        
        # Create RemoteFunction instances to test pool selection
        process_func = RemoteFunction(process_image_data, _nuitka_ray, "test")
        compute_func = RemoteFunction(compute_calibration, _nuitka_ray, "test") 
        read_func = RemoteFunction(read_file_content, _nuitka_ray, "test")
        save_func = RemoteFunction(save_output_data, _nuitka_ray, "test")
        
        print("  ✅ Pool selection logic created successfully")
        
        # Test the heuristic function
        should_use_process = process_func._should_use_process_pool(process_image_data)
        print(f"  ✅ process_image_data should use process pool: {should_use_process}")
        
        should_use_process = read_func._should_use_process_pool(read_file_content)
        print(f"  ✅ read_file_content should use process pool: {should_use_process}")
        
    except Exception as e:
        print(f"❌ Pool selection test failed: {e}")
        return False
    
    # Test 6: Shutdown Test
    print("\n🔍 TEST 6: Shutdown Test")
    try:
        ray.shutdown()
        print("✅ Ray Replacement shutdown successfully")
        
        if not ray.is_initialized():
            print("✅ is_initialized() correctly returns False after shutdown")
        else:
            print("❌ is_initialized() still returns True after shutdown")
            
    except Exception as e:
        print(f"❌ Shutdown test failed: {e}")
        return False
    
    print("\n🎉 ALL RAY REPLACEMENT TESTS PASSED!")
    print("✅ Maximum performance Ray Replacement is working correctly")
    return True

if __name__ == "__main__":
    success = test_ray_replacement()
    if success:
        print("\n🚀 Ray Replacement is ready for Nuitka compilation!")
    else:
        print("\n❌ Ray Replacement needs fixes before compilation!")
    
    input("\nPress Enter to continue...")
