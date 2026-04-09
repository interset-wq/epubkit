from .converter import MarkdownToEPUB, HTMLToEPUB
from .core import EPUBConverter
from .utils import clean_filename, get_title_from_file
from typing import Optional
import os

def HTML2EPUB(html_file_path: str, output_path: Optional[str] = None, author: str = "Unknown", language: str = "en") -> str:
    """
    Convert a single HTML file to EPUB.
    
    Args:
        html_file_path: Path to the HTML file
        output_path: Output path for the EPUB file. If not provided, will use the title or h1 or filename
        author: Author name (default: "Unknown")
        language: Language code (default: "en")
    
    Returns:
        The path to the generated EPUB file
    """
    # Create converter without title - it will be extracted from HTML
    converter = HTMLToEPUB(title=None, author=author, language=language)
    
    # Add the HTML file as a chapter
    converter.add_chapter("Chapter 1", html_file_path)
    
    # Determine output filename
    if output_path is None:
        # Try to get title from HTML, fallback to filename
        title = get_title_from_file(html_file_path)
        
        # If no title found, use filename without extension
        if not title:
            title = os.path.splitext(os.path.basename(html_file_path))[0]
        
        # Clean title for filename (remove special characters)
        clean_title = clean_filename(title)
        
        output_path = f"{clean_title}.epub"
    
    # Generate the EPUB
    converter.generate(output_path)
    
    return output_path

def Markdown2EPUB(markdown_file_path: str, title: Optional[str] = None, output_path: Optional[str] = None, author: str = "Unknown", language: str = "en") -> str:
    """
    Convert a single Markdown file to EPUB.
    
    Args:
        markdown_file_path: Path to the Markdown file
        title: Title of the EPUB. If not provided, will use the first heading or filename
        output_path: Output path for the EPUB file. If not provided, will use the title or filename
        author: Author name (default: "Unknown")
        language: Language code (default: "en")
    
    Returns:
        The path to the generated EPUB file
    """
    # Determine title if not provided
    if not title:
        # Try to get title from Markdown file
        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for first heading
                import re
                match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
                if match:
                    title = match.group(1).strip()
                else:
                    # Fallback to filename
                    title = os.path.splitext(os.path.basename(markdown_file_path))[0]
        except Exception:
            # Fallback to filename
            title = os.path.splitext(os.path.basename(markdown_file_path))[0]
    
    # Create converter
    converter = MarkdownToEPUB(title=title, author=author, language=language)
    
    # Add the Markdown file as a chapter
    converter.add_chapter("Chapter 1", markdown_file_path)
    
    # Determine output filename
    if output_path is None:
        # Clean title for filename
        clean_title = clean_filename(title)
        output_path = f"{clean_title}.epub"
    
    # Generate the EPUB
    converter.generate(output_path)
    
    return output_path

__version__ = "0.1.0"
__all__ = ["EPUBConverter", "MarkdownToEPUB", "HTMLToEPUB", "HTML2EPUB", "Markdown2EPUB", "clean_filename", "get_title_from_file"]
