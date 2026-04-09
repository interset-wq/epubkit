#!/usr/bin/env python3
"""
Unit tests for epubkit library
"""

import os
import unittest
import tempfile
from epubkit import HTML2EPUB, Markdown2EPUB, clean_filename, get_title_from_file


class TestEpubkit(unittest.TestCase):
    """Test cases for epubkit library"""

    def setUp(self):
        """Set up test files"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_clean_filename(self):
        """Test clean_filename function"""
        test_cases = [
            ("Test Book Title", "Test-Book-Title"),
            ("Test@#$%^&*()Book", "TestBook"),
            ("  Test Book  ", "Test-Book"),
            ("Test-Book", "Test-Book"),
        ]
        
        for input_str, expected in test_cases:
            result = clean_filename(input_str)
            self.assertEqual(result, expected)

    def test_get_title_from_file(self):
        """Test get_title_from_file function"""
        # Create a test HTML file with title
        html_content = """
        <html>
        <head>
            <title>Test HTML Title</title>
        </head>
        <body>
            <h1>Test H1 Title</h1>
            <p>Test content</p>
        </body>
        </html>
        """
        html_file = os.path.join(self.temp_dir, "test.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Test getting title from title tag
        title = get_title_from_file(html_file)
        self.assertEqual(title, "Test HTML Title")

    def test_markdown_to_epub(self):
        """Test Markdown2EPUB function"""
        # Create a test Markdown file
        md_content = """
        # Test Markdown Book

        This is a test Markdown book.

        ## Chapter 1

        This is chapter 1.

        ## Chapter 2

        This is chapter 2.
        """
        md_file = os.path.join(self.temp_dir, "test.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Convert to EPUB
        output_path = Markdown2EPUB(md_file, title="Test Markdown Book", author="Test Author")
        
        # Check if EPUB file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".epub"))
        
        # Clean up
        os.remove(output_path)

    def test_html_to_epub(self):
        """Test HTML2EPUB function"""
        # Create a test HTML file
        html_content = """
        <html>
        <head>
            <title>Test HTML Book</title>
        </head>
        <body>
            <h1>Test HTML Book</h1>
            <p>This is a test HTML book.</p>
            <h2>Chapter 1</h2>
            <p>This is chapter 1.</p>
            <h2>Chapter 2</h2>
            <p>This is chapter 2.</p>
        </body>
        </html>
        """
        html_file = os.path.join(self.temp_dir, "test.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Convert to EPUB
        output_path = HTML2EPUB(html_file, author="Test Author")
        
        # Check if EPUB file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".epub"))
        
        # Clean up
        os.remove(output_path)


if __name__ == "__main__":
    unittest.main()
