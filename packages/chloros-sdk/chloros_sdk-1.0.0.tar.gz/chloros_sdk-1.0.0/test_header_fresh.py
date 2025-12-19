#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test header with no caching issues"""

import sys
import os
import io

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# Clear any cached imports
for key in list(sys.modules.keys()):
    if 'cli_styles' in key or 'cli_i18n' in key:
        del sys.modules[key]

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Now import fresh
import cli_styles
from cli_styles import print_header

print("Testing header from cli_styles.py...")
print("=" * 80)
print()

# Display the header
print_header("MAPIR CHLOROS+ Command Line Interface", "1.0.1")

print()
print("=" * 80)











