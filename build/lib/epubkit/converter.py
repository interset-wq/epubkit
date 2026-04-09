import os
import markdown
from bs4 import BeautifulSoup
from typing import Optional
from .core import EPUBConverter
from .utils import generate_image_filename

class MarkdownToEPUB(EPUBConverter):
    def __init__(self, title: str, author: str = "Unknown", language: str = "en"):
        super().__init__(title, author, language)
    
    def _process_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(md_content)
        
        # Add ids to headings for table of contents
        soup = BeautifulSoup(html_content, 'html.parser')
        self._extract_headings(soup)
        
        # Add style sheet reference
        wrapped_content = self._wrap_html(str(soup))
        return wrapped_content
    
    def _extract_headings(self, soup):
        # Extract headings (h1-h6) for table of contents
        self.headings = []
        heading_id = 1
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            text = heading.get_text().strip()
            # Generate unique id for each heading
            heading_id_str = f'heading{heading_id}'
            heading['id'] = heading_id_str
            self.headings.append((level, text, heading_id_str))
            heading_id += 1

class HTMLToEPUB(EPUBConverter):
    def __init__(self, title: Optional[str] = None, author: str = "Unknown", language: str = "en"):
        # If title is not provided, it will be extracted from HTML
        super().__init__(title or "Untitled", author, language)
        self.extracted_title: Optional[str] = None
    
    def _process_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Remove HTML comments
        import re
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title from HTML if not provided
        if not self.title or self.title == "Untitled":
            title_tag = soup.find('title')
            if title_tag and title_tag.get_text().strip():
                self.extracted_title = title_tag.get_text().strip()
                self.title = self.extracted_title
            else:
                # Try to find h1 as title
                h1_tag = soup.find('h1')
                if h1_tag and h1_tag.get_text().strip():
                    self.extracted_title = h1_tag.get_text().strip()
                    self.title = self.extracted_title
        
        # Create a new soup for clean content
        clean_soup = BeautifulSoup('<body></body>', 'html.parser')
        body = clean_soup.body
        
        # Find all headings and their following content
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        # Extract headings and content
        self.headings = []
        heading_id = 1
        
        # List to store images that need to be downloaded
        self.images = []
        image_id = 1
        
        # Debug: Find all images in the HTML
        all_images = soup.find_all('img')
        print(f"Found {len(all_images)} images in HTML")
        for img in all_images[:5]:  # Show first 5 images
            if 'src' in img.attrs:
                print(f"  Image src: {img['src']}")
        
        # Process all images first
        import os
        for img in all_images:
            if 'src' in img.attrs:
                src = img['src']
                # Check if it's a remote image
                if src.startswith('http://') or src.startswith('https://'):
                    # Generate a local filename with a proper extension
                    # Default extension
                    ext = '.png'
                    # Try to extract extension from URL
                    if '.' in src:
                        # Get the part after the last dot
                        last_part = src.split('.')[-1]
                        # Take the first 4 characters to get the extension
                        potential_ext = last_part.split('?')[0].split('#')[0][:4].lower()
                        if potential_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                            ext = f'.{potential_ext}'
                        elif potential_ext.startswith('jpg'):
                            ext = '.jpg'
                    # Generate a clean filename
                    image_filename = f'image{image_id}{ext}'
                    # Add to images list
                    self.images.append((src, image_filename))
                    # Update src to local path
                    img['src'] = f'../images/{image_filename}'
                    image_id += 1
                else:
                    # Local image
                    # Check if the file exists
                    local_path = os.path.join(os.path.dirname(file_path), src)
                    print(f"Processing local image: {src}")
                    print(f"Local path: {local_path}")
                    print(f"File exists: {os.path.exists(local_path)}")
                    if os.path.exists(local_path):
                        # Generate a local filename
                        image_filename = f'image{image_id}.{os.path.basename(src).split('.')[-1]}'
                        # Add to images list
                        self.images.append((local_path, image_filename))
                        # Update src to local path
                        img['src'] = f'../images/{image_filename}'
                        image_id += 1
                        print(f"Added image to list: {local_path} -> {image_filename}")
                    else:
                        # Local image doesn't exist, keep as is
                        print(f"Image not found, keeping as is: {src}")
        
        # Debug: Check images list
        print(f"Total images to process: {len(self.images)}")
        for src, filename in self.images:
            print(f"  Image: {src} -> {filename}")
        
        for heading in headings:
            # Get the heading text and level
            level = int(heading.name[1])
            text = heading.get_text().strip()
            
            # Skip unwanted headings
            if text in ['Add to collection', 'In this article', 'Table of contents']:
                continue
            
            # Skip empty headings
            if not text:
                continue
            
            # Create a new heading element
            new_heading = clean_soup.new_tag(heading.name)
            new_heading['id'] = f'heading{heading_id}'
            
            # Remove any links inside the heading
            if heading.find('a'):
                # Just use the text content, not the link
                new_heading.string = text
            else:
                # Copy the original text
                new_heading.string = text
            
            # Add the heading to the clean soup
            body.append(new_heading)
            
            # Add to headings list
            self.headings.append((level, text, f'heading{heading_id}'))
            heading_id += 1
            
            # Get the next siblings until the next heading
            sibling = heading.next_sibling
            while sibling:
                # If this is a new heading, stop
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
                
                # Process the sibling
                if hasattr(sibling, 'name'):
                    # Only include certain elements
                    if sibling.name in ['p', 'ul', 'ol', 'li', 'code', 'pre', 'img', 'table', 'tr', 'td', 'th']:
                        # Create a new element
                        new_element = clean_soup.new_tag(sibling.name)
                        
                        # Copy all attributes
                        for attr, value in sibling.attrs.items():
                            new_element[attr] = value
                        
                        # Copy the content
                        if sibling.string:
                            new_element.string = sibling.string
                        else:
                            # Copy children
                            for child in sibling.children:
                                if hasattr(child, 'name') and child.name:
                                    new_child = clean_soup.new_tag(child.name)
                                    if child.string:
                                        new_child.string = child.string
                                    # Copy attributes for images
                                    if child.name == 'img':
                                        if 'src' in child.attrs:
                                            src = child['src']
                                            # Check if it's a remote image
                                            if src.startswith('http://') or src.startswith('https://'):
                                                # Generate a local filename
                                                image_filename = f'image{image_id}.{src.split('.')[-1].split('?')[0].split('#')[0]}'
                                                # Add to images list
                                                self.images.append((src, image_filename))
                                                # Update src to local path
                                                new_child['src'] = f'../images/{image_filename}'
                                                image_id += 1
                                            else:
                                                # Local image, keep as is
                                                new_child['src'] = src
                                        if 'alt' in child.attrs:
                                            new_child['alt'] = child['alt']
                                    new_element.append(new_child)
                                elif child.string:
                                    new_element.append(child)
                        
                        # Add to clean soup
                        body.append(new_element)
                
                # Move to next sibling
                sibling = sibling.next_sibling
        
        # Create a clean HTML structure
        clean_html = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8"/>
    <title>{self.title}</title>
    <link rel="stylesheet" href="style.css"/>
</head>
<body>
{body.decode_contents()}
</body>
</html>'''
        
        # Clean up HTML tags, removing all attributes except for necessary ones
        soup_clean = BeautifulSoup(clean_html, 'html.parser')
        self._clean_tags(soup_clean)
        
        # Return the cleaned HTML
        return str(soup_clean)
    
    def _extract_headings(self, soup):
        # Extract headings (h1-h6) for table of contents
        self.headings = []
        heading_id = 1
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            text = heading.get_text().strip()
            # Generate unique id for each heading
            heading_id_str = f'heading{heading_id}'
            heading['id'] = heading_id_str
            self.headings.append((level, text, heading_id_str))
            heading_id += 1
    
    def _clean_tags(self, soup):
        # List of tags that can have href attribute
        href_tags = ['a']
        # List of tags that can have src attribute
        src_tags = ['img', 'script', 'iframe']
        # List of tags that can have alt attribute
        alt_tags = ['img']
        # List of tags that can have id attribute
        id_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'section']
        
        for tag in soup.find_all(True):
            # Keep only necessary attributes
            new_attrs = {}
            
            if tag.name in href_tags and 'href' in tag.attrs:
                new_attrs['href'] = tag['href']
            
            if tag.name in src_tags and 'src' in tag.attrs:
                new_attrs['src'] = tag['src']
            
            if tag.name in alt_tags and 'alt' in tag.attrs:
                new_attrs['alt'] = tag['alt']
            
            if tag.name in id_tags and 'id' in tag.attrs:
                new_attrs['id'] = tag['id']
            
            # Keep link tags for stylesheets
            if tag.name == 'link':
                if 'rel' in tag.attrs:
                    new_attrs['rel'] = tag['rel']
                if 'href' in tag.attrs:
                    new_attrs['href'] = tag['href']
            
            # Replace attributes
            tag.attrs = new_attrs
        
        # Remove links inside headings to avoid interference with anchor jumps
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            for a in heading.find_all('a'):
                # Replace link with just the text
                a.unwrap()
