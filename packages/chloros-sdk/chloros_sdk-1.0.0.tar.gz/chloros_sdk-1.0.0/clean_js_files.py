#!/usr/bin/env python3
"""Clean debug console.errors from JavaScript files"""

import re

# Clean SSE client
with open('ui/js/sse-client.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the specific error handler at line 451
content = content.replace(
    "            this.eventSource.onerror = (event) => {\n"
    "                console.error('[SSE] Connection error:', event);\n"
    "                this.isConnected = false;",
    "            this.eventSource.onerror = (event) => {\n"
    "                // Connection error (suppressed for clean console)\n"
    "                this.isConnected = false;"
)

# Also suppress the other verbose error handler
content = content.replace(
    "            this.eventSource.onerror = (event) => {\n"
    "                console.error('[SSE] ❌ Connection error occurred!');\n"
    "                console.error('[SSE] ❌ Error event:', event);\n"
    "                console.error('[SSE] ❌ EventSource readyState:', this.eventSource.readyState);\n"
    "                console.error('[SSE] ❌ EventSource url:', this.eventSource.url);\n"
    "                this.isConnected = false;",
    "            this.eventSource.onerror = (event) => {\n"
    "                // Connection error details suppressed for clean console\n"
    "                this.isConnected = false;"
)

with open('ui/js/sse-client.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ SSE client cleaned')
