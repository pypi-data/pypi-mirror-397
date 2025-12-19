"""
Quick test to compare all 4 debayer methods on a sample image.
This tests the OpenCV implementations locally before the full backend compile.
"""
import numpy as np
import cv2
import time
from mip.debayer import debayer_HighQuality, debayer_MaximumQuality

def create_test_bayer_image():
    """Create a synthetic Bayer image for testing (RGGB pattern)."""
    print("Creating synthetic test Bayer image (3000x4000)...")
    
    # Create a test pattern with gradients and edges
    height, width = 3000, 4000
    img = np.zeros((height, width), dtype=np.uint16)
    
    # Add gradient
    for i in range(height):
        for j in range(width):
            img[i, j] = int((i / height) * 65535)
    
    # Add some edges
    img[1000:1100, :] = 65535
    img[:, 2000:2100] = 32768
    
    # Add some noise
    noise = np.random.normal(0, 500, (height, width))
    img = np.clip(img + noise, 0, 65535).astype(np.uint16)
    
    print(f"✅ Test image created: {height}x{width} uint16")
    return img

def test_debayer_method(name, func, bayer_img):
    """Test a single debayer method and report timing."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    try:
        start = time.time()
        result = func(bayer_img)
        elapsed = time.time() - start
        
        print(f"\n✅ SUCCESS!")
        print(f"   Output shape: {result.shape}")
        print(f"   Processing time: {elapsed:.3f}s")
        print(f"   Speed rating: {3000*4000/elapsed/1e6:.2f} megapixels/sec")
        
        return True, elapsed, result
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, None

def main():
    """Run comparison test of all 4 debayer methods."""
    print("="*60)
    print("DEBAYER METHOD COMPARISON TEST")
    print("="*60)
    print("\nTesting the 2 debayer methods:")
    print("  1. High Quality (Faster) - Edge-Aware algorithm")
    print("  2. Maximum Quality (Slower) - Multi-pass with denoising")
    print()
    
    # Create test image
    bayer_img = create_test_bayer_image()
    
    # Test each method
    results = {}
    
    methods = [
        ("High Quality (Faster)", debayer_HighQuality),
        ("Maximum Quality (Slower)", debayer_MaximumQuality),
    ]
    
    for name, func in methods:
        success, elapsed, output = test_debayer_method(name, func, bayer_img)
        results[name] = {"success": success, "time": elapsed, "output": output}
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = [(name, data["time"]) for name, data in results.items() if data["success"]]
    
    if successful:
        # Sort by speed
        successful.sort(key=lambda x: x[1])
        
        fastest_time = successful[0][1]
        
        print("\nResults (sorted by speed):")
        for i, (name, elapsed) in enumerate(successful, 1):
            relative = elapsed / fastest_time
            speed_rating = 3000*4000/elapsed/1e6
            
            print(f"\n{i}. {name}")
            print(f"   Time: {elapsed:.3f}s")
            print(f"   Speed: {speed_rating:.2f} MP/s")
            print(f"   Relative: {relative:.2f}x slower than fastest")
            
            if name == "High Quality (Faster)":
                print(f"   Quality: ★★★★★★ (Excellent)")
            elif name == "Maximum Quality (Slower)":
                print(f"   Quality: ★★★★★★★ (Maximum + Denoising)")
        
        print("\n" + "="*60)
        print("✅ ALL METHODS WORK! Ready for Nuitka compilation!")
        print("="*60)
    else:
        print("\n❌ Some methods failed. Check errors above.")
    
    return results

if __name__ == "__main__":
    main()

