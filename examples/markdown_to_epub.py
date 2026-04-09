#!/usr/bin/env python3
"""
Example: Convert Markdown to EPUB
"""

from epubkit import Markdown2EPUB

# Create a test Markdown file
markdown_content = """
# My Markdown Book

This is a sample Markdown book.

## Chapter 1

This is the first chapter.

## Chapter 2

This is the second chapter.

## Conclusion

This is the conclusion.
"""

# Write to a file
with open('sample.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

# Convert to EPUB
output = Markdown2EPUB('sample.md', title="My Markdown Book", author="John Doe")
print(f"EPUB created: {output}")
