#!/usr/bin/env python3
"""
Example: Convert HTML to EPUB with custom author and output path
"""

from epubkit import HTML2EPUB

# Convert HTML to EPUB with custom author and output path
output = HTML2EPUB('example.html', author="Jane Smith", output_path="my_article.epub")
print(f"EPUB created: {output}")
