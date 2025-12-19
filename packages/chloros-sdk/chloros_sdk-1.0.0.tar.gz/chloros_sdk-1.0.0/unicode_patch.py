#!/usr/bin/env python3
"""
Unicode patch to handle encoding issues in api.py
"""
import sys
import re
import codecs

# Set the default encoding to UTF-8
if hasattr(sys, 'setdefaultencoding'):
    sys.setdefaultencoding('utf-8')

# Override stdout/stderr to handle Unicode properly (only if they exist)
if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Monkey patch print to handle Unicode safely
original_print = print

def safe_print(*args, **kwargs):
    """Print function that handles Unicode encoding errors"""
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        # Clean args of problematic Unicode characters
        cleaned_args = []
        for arg in args:
            if isinstance(arg, str):
                # Remove non-ASCII characters
                cleaned = re.sub(r'[^\x00-\x7F]+', '?', arg)
                cleaned_args.append(cleaned)
            else:
                cleaned_args.append(arg)
        original_print(*cleaned_args, **kwargs)
    except Exception:
        # Last resort: convert everything to string and strip non-ASCII
        try:
            safe_args = [re.sub(r'[^\x00-\x7F]+', '?', str(arg)) for arg in args]
            original_print(*safe_args, **kwargs)
        except:
            pass  # Give up silently

# Apply the patch
import builtins
builtins.print = safe_print
