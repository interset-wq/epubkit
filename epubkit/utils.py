import os
import re
from typing import Optional


def clean_filename(name: str) -> str:
    """
    Clean a string to make it suitable for use as a filename.
    
    Args:
        name: The string to clean
        
    Returns:
        A cleaned string suitable for use as a filename
    """
    # Remove special characters
    clean_name = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace spaces and hyphens with a single hyphen
    clean_name = re.sub(r'[-\s]+', '-', clean_name)
    return clean_name


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: The filename
        
    Returns:
        The file extension (without the dot)
    """
    return os.path.splitext(filename)[1][1:].lower()


def get_title_from_html(html_content: str) -> Optional[str]:
    """
    Extract the title from HTML content.
    
    Args:
        html_content: The HTML content
        
    Returns:
        The extracted title, or None if no title found
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to get title from title tag
    title_tag = soup.find('title')
    if title_tag and title_tag.get_text().strip():
        return title_tag.get_text().strip()
    
    # Try to get title from h1 tag
    h1_tag = soup.find('h1')
    if h1_tag and h1_tag.get_text().strip():
        return h1_tag.get_text().strip()
    
    return None


def get_title_from_file(file_path: str) -> Optional[str]:
    """
    Extract the title from an HTML file.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        The extracted title, or None if no title found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return get_title_from_html(html_content)
    except Exception:
        return None


def generate_image_filename(url: str, index: int) -> str:
    """
    Generate a filename for an image based on its URL and index.
    
    Args:
        url: The image URL
        index: The image index
        
    Returns:
        A generated filename for the image
    """
    # Default extension
    ext = '.png'
    
    # Try to extract extension from URL
    if '.' in url:
        # Get the part after the last dot
        last_part = url.split('.')[-1]
        # Take the first 4 characters to get the extension
        potential_ext = last_part.split('?')[0].split('#')[0][:4].lower()
        if potential_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
            ext = f'.{potential_ext}'
        elif potential_ext.startswith('jpg'):
            ext = '.jpg'
    
    return f'image{index}{ext}'