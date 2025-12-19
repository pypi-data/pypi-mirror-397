import sys
import os
import datetime

# Test the StdoutTee implementation
log_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Chloros', 'logs')
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f'test_{timestamp}.log')

print(f"Test log file: {log_file}")
print(f"Original stdout: {sys.__stdout__}")

class StdoutTee:
    """Redirect stdout to both console and log file"""
    def __init__(self, log_file_path):
        self.terminal = sys.__stdout__
        try:
            self.log = open(log_file_path, 'a', encoding='utf-8', buffering=1)
            self.log_enabled = True
            self.log.write(f"[LOG-INIT] Log file opened: {log_file_path}\n")
            self.log.flush()
            self.terminal.write(f"[LOG-INIT] Successfully opened log file\n")
        except Exception as e:
            self.log_enabled = False
            self.terminal.write(f"[LOG-INIT] ERROR: {e}\n")
    
    def write(self, message):
        # Terminal
        try:
            self.terminal.write(message)
            self.terminal.flush()
        except:
            pass
        
        # Log file
        if self.log_enabled:
            try:
                self.log.write(message)
                self.log.flush()
            except Exception as e:
                self.log_enabled = False
                self.terminal.write(f"[LOG-ERROR] {e}\n")
    
    def flush(self):
        try:
            self.terminal.flush()
        except:
            pass
        if self.log_enabled:
            try:
                self.log.flush()
            except:
                pass

# Install the tee
sys.stdout = StdoutTee(log_file)

# Test writing
print("=" * 60)
print("TEST MESSAGE 1")
print("TEST MESSAGE 2")
print("TEST MESSAGE 3")
print("=" * 60)
sys.stdout.flush()

# Wait a moment
import time
time.sleep(0.5)

# Check file size
size = os.path.getsize(log_file)
print(f"\nLog file size: {size} bytes")

if size > 0:
    print("✅ SUCCESS: Log file has content!")
    with open(log_file, 'r', encoding='utf-8') as f:
        print(f"\nLog file contents:\n{f.read()}")
else:
    print("❌ FAILED: Log file is empty!")



