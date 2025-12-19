#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that browser mode logging is working correctly
This simulates the logging setup and verifies that print statements are captured
"""

import sys
import os
import tempfile
import time

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_stdout_tee():
    """Test that StdoutTee captures both console and file output"""
    
    print("=" * 60)
    print("Testing Browser Mode Logging Fix")
    print("=" * 60)
    print()
    
    # Create a temporary log file
    temp_dir = tempfile.gettempdir()
    log_file = os.path.join(temp_dir, f'chloros_test_log_{int(time.time())}.txt')
    
    print(f"Test log file: {log_file}")
    print()
    
    # Simulate the StdoutTee class from backend_server.py
    class StdoutTee:
        """Redirect stdout to both console and log file"""
        def __init__(self, log_file_path):
            self.terminal = sys.__stdout__  # Keep reference to original stdout
            self.log = open(log_file_path, 'a', encoding='utf-8', buffering=1)  # Line buffered
        
        def write(self, message):
            # Write to both terminal and log file
            try:
                self.terminal.write(message)
                self.terminal.flush()
                self.log.write(message)
                self.log.flush()
            except Exception:
                pass  # Silently ignore errors to prevent infinite loops
        
        def flush(self):
            try:
                self.terminal.flush()
                self.log.flush()
            except Exception:
                pass
    
    # Redirect stdout
    original_stdout = sys.stdout
    print("1. Installing stdout redirection...")
    sys.stdout = StdoutTee(log_file)
    
    # These prints should go to both console AND log file
    print("2. Testing print statements (AFTER redirection)...")
    print("   [OK] This should appear in console")
    print("   [OK] This should appear in log file")
    print()
    
    print("3. Testing multiple lines:")
    for i in range(3):
        print(f"   Line {i+1}")
    print()
    
    print("4. Testing special characters:")
    print("   [CHECK] Checkmark")
    print("   [X] X mark")
    print("   [WARN] Warning")
    print("   [ROCKET] Rocket")
    print()
    
    # Flush to ensure everything is written
    sys.stdout.flush()
    
    # Restore original stdout for reading the file
    sys.stdout = original_stdout
    
    print("5. Verifying log file contents...")
    print()
    
    # Read and display the log file
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_contents = f.read()
        
        print("=" * 60)
        print("LOG FILE CONTENTS:")
        print("=" * 60)
        print(log_contents)
        print("=" * 60)
        print()
        
        # Verify that expected content is in the log
        expected_strings = [
            "Testing print statements (AFTER redirection)",
            "[OK] This should appear in log file",
            "Testing multiple lines",
            "Line 1",
            "Line 2", 
            "Line 3",
            "Testing special characters",
            "[CHECK] Checkmark"
        ]
        
        missing = []
        for expected in expected_strings:
            if expected not in log_contents:
                missing.append(expected)
        
        if missing:
            print("❌ TEST FAILED!")
            print(f"   Missing from log file: {missing}")
            return False
        else:
            print("✅ TEST PASSED!")
            print("   All print statements were captured in the log file")
            print()
            print(f"   Log file size: {len(log_contents)} bytes")
            print(f"   Log file lines: {log_contents.count(chr(10))} lines")
            return True
            
    except Exception as e:
        print(f"❌ TEST FAILED: Error reading log file: {e}")
        return False
    finally:
        # Clean up
        try:
            os.remove(log_file)
            print(f"\n   Cleaned up test file: {log_file}")
        except:
            pass

if __name__ == '__main__':
    success = test_stdout_tee()
    sys.exit(0 if success else 1)



