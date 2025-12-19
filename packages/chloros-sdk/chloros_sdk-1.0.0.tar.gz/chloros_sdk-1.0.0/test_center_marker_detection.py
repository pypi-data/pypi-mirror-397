"""
Test script for T4P-R25M center marker detection
Tests white blob, Hough circle, and template matching methods

Usage:
    python test_center_marker_detection.py <image_path>
    
    Or test on all images in a folder:
    python test_center_marker_detection.py <folder_path>
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path

# Import detection functions
try:
    from mip.Calibration_Target import (
        detect_center_marker_white_blob,
        detect_center_marker_hough_circle,
        detect_center_marker_template,
        detect_center_marker_multi_method,
        detect_calibration_targets,
        calibration_target_polys,
        center_marker_config
    )
    print("✅ Successfully imported detection functions from mip.Calibration_Target")
except ImportError as e:
    print(f"❌ Error importing from mip.Calibration_Target: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Import LabImage if available
try:
    from project import LabImage
    print("✅ Successfully imported LabImage from project")
except ImportError:
    print("⚠️ Warning: Could not import LabImage, using simplified testing")
    LabImage = None


def create_test_marker_image(size=500, outer_diameter=100, inner_diameter=80):
    """
    Create a synthetic test image with a center marker
    """
    img = np.ones((size, size), dtype=np.uint8) * 128  # Grey background
    center = (size // 2, size // 2)
    
    # Draw black circle
    cv2.circle(img, center, outer_diameter // 2, 50, -1)
    
    # Draw white center dot
    cv2.circle(img, center, inner_diameter // 2, 255, -1)
    
    return img


def test_detection_methods_on_region(image_region, outer_diameter_px, inner_diameter_px, name="test"):
    """
    Test all three detection methods on an image region
    """
    print(f"\n{'='*60}")
    print(f"Testing detection methods on: {name}")
    print(f"Region shape: {image_region.shape}")
    print(f"Expected outer diameter: {outer_diameter_px}px")
    print(f"Expected inner diameter: {inner_diameter_px}px")
    print(f"{'='*60}\n")
    
    results = {}
    
    # Test Method 1: White Blob Detection
    print("=" * 60)
    print("METHOD 1: White Blob Detection")
    print("=" * 60)
    success, offset_x, offset_y, confidence = detect_center_marker_white_blob(
        image_region, inner_diameter_px, debug=True
    )
    results['white_blob'] = {
        'success': success,
        'offset': (offset_x, offset_y),
        'confidence': confidence
    }
    
    # Test Method 2: Hough Circle Detection
    print("\n" + "=" * 60)
    print("METHOD 2: Hough Circle Detection")
    print("=" * 60)
    success, offset_x, offset_y, confidence = detect_center_marker_hough_circle(
        image_region, outer_diameter_px, inner_diameter_px, debug=True
    )
    results['hough_circle'] = {
        'success': success,
        'offset': (offset_x, offset_y),
        'confidence': confidence
    }
    
    # Test Method 3: Template Matching
    print("\n" + "=" * 60)
    print("METHOD 3: Template Matching")
    print("=" * 60)
    success, offset_x, offset_y, confidence = detect_center_marker_template(
        image_region, outer_diameter_px, inner_diameter_px, debug=True
    )
    results['template'] = {
        'success': success,
        'offset': (offset_x, offset_y),
        'confidence': confidence
    }
    
    # Test Multi-Method (best result)
    print("\n" + "=" * 60)
    print("COMBINED: Multi-Method Detection")
    print("=" * 60)
    success, offset_x, offset_y, method = detect_center_marker_multi_method(
        image_region, outer_diameter_px, inner_diameter_px, debug=True
    )
    results['multi_method'] = {
        'success': success,
        'offset': (offset_x, offset_y),
        'method': method
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for method_name, result in results.items():
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        if method_name == 'multi_method':
            print(f"{method_name:15} : {status} - Best method: {result.get('method', 'none')}")
        else:
            conf = result.get('confidence', 0)
            print(f"{method_name:15} : {status} - Confidence: {conf:.3f}")
    
    return results


def test_synthetic_images():
    """
    Test detection on synthetic images with various dot sizes
    """
    print("\n" + "🧪" * 30)
    print("TESTING ON SYNTHETIC IMAGES")
    print("🧪" * 30)
    
    # Test different white dot sizes (as per user's question)
    test_configs = [
        {"outer": 120, "inner": 100, "name": "10mm white / 1mm black (Current design)"},
        {"outer": 120, "inner": 96, "name": "8mm white / 2mm black"},
        {"outer": 120, "inner": 72, "name": "6mm white / 3mm black (Recommended)"},
        {"outer": 120, "inner": 48, "name": "4mm white / 4mm black (Conservative)"},
        {"outer": 120, "inner": 24, "name": "2mm white / 5mm black (Extreme)"},
    ]
    
    all_results = {}
    
    for config in test_configs:
        print(f"\n{'🔬'*30}")
        print(f"Testing: {config['name']}")
        print(f"{'🔬'*30}")
        
        img = create_test_marker_image(500, config['outer'], config['inner'])
        results = test_detection_methods_on_region(
            img, config['outer'], config['inner'], config['name']
        )
        all_results[config['name']] = results
    
    # Final comparison
    print("\n" + "📊" * 30)
    print("FINAL COMPARISON - Which dot size works best?")
    print("📊" * 30)
    
    for config_name, results in all_results.items():
        print(f"\n{config_name}:")
        multi_result = results['multi_method']
        if multi_result['success']:
            print(f"  ✅ DETECTED - Method: {multi_result['method']}")
        else:
            print(f"  ❌ FAILED - All methods failed")


def test_real_calibration_image(image_path):
    """
    Test detection on a real calibration image with T4P-R25M target
    """
    print(f"\n{'📷'*30}")
    print(f"TESTING ON REAL IMAGE: {image_path}")
    print(f"{'📷'*30}\n")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return
    
    # Try to use LabImage if available
    if LabImage is not None:
        try:
            # Create a minimal project-like object
            class MinimalProject:
                def __init__(self):
                    self.data = {'config': {'Project Settings': {'Processing': {}}}}
                    self.path = os.path.dirname(image_path)
                
                def get_config(self, section, key):
                    return None
            
            project = MinimalProject()
            image = LabImage(project, image_path)
            
            # Detect ArUco marker
            print("🔍 Detecting ArUco marker...")
            detected = detect_calibration_targets(image)
            
            if detected:
                print(f"✅ ArUco marker detected: ID {image.aruco_id}")
                
                if image.aruco_id == 47:
                    print("✅ Confirmed T4P-R25M target (ArUco ID 47)")
                    
                    # Calculate calibration target polygons (this will use our new detection)
                    print("\n🎯 Calculating calibration target polygons with center marker detection...")
                    calibration_target_polys(image)
                    
                    if hasattr(image, 'center_marker_detection_method'):
                        print(f"\n✅ Detection method used: {image.center_marker_detection_method}")
                    
                    print("\n" + "="*60)
                    print("SUCCESS! Center marker detection completed.")
                    print("="*60)
                    
                else:
                    print(f"⚠️ Warning: This is not a T4P-R25M target (found ArUco ID {image.aruco_id})")
                    print("   The center marker detection is only for T4P-R25M (ArUco ID 47)")
            else:
                print("❌ No ArUco marker detected in image")
                
        except Exception as e:
            print(f"❌ Error processing image with LabImage: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Fallback: just load image and test on a manual region
        print("⚠️ LabImage not available, testing on image center region")
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"❌ Error: Could not load image from {image_path}")
            return
        
        # Extract center region (assuming marker is roughly in center)
        h, w = img.shape
        size = min(h, w) // 4
        center_y, center_x = h // 2, w // 2
        region = img[center_y - size:center_y + size, center_x - size:center_x + size]
        
        # Estimate marker size as ~10% of region
        estimated_outer = size * 0.2
        estimated_inner = size * 0.17
        
        results = test_detection_methods_on_region(
            region, estimated_outer, estimated_inner, os.path.basename(image_path)
        )


def main():
    """
    Main test function
    """
    print("=" * 70)
    print(" T4P-R25M CENTER MARKER DETECTION TEST SUITE")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\n📝 No image path provided, running synthetic image tests...\n")
        test_synthetic_images()
        
        print("\n" + "="*70)
        print("To test on real images, run:")
        print("  python test_center_marker_detection.py <image_path>")
        print("  python test_center_marker_detection.py <folder_path>")
        print("="*70)
    else:
        path = sys.argv[1]
        
        if os.path.isfile(path):
            # Test single image
            test_real_calibration_image(path)
        elif os.path.isdir(path):
            # Test all images in folder
            image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.JPG', '.JPEG'}
            image_files = [f for f in Path(path).iterdir() 
                          if f.suffix in image_extensions]
            
            if not image_files:
                print(f"❌ No image files found in {path}")
                return
            
            print(f"\n📁 Found {len(image_files)} images in folder")
            for img_file in image_files:
                test_real_calibration_image(str(img_file))
        else:
            print(f"❌ Error: Path not found: {path}")
    
    print("\n" + "="*70)
    print(" TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

























