#!/usr/bin/env python3
"""
Basic example: Convert HTML to EPUB
"""

from epubkit import HTML2EPUB

# Convert HTML to EPUB
output = HTML2EPUB('example.html')
print(f"EPUB created: {output}")
