import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Tuple, Optional
import requests
from PIL import Image, ImageDraw, ImageFont

class EPUBConverter:
    def __init__(self, title: str, author: str, language: str = "en"):
        self.title = title
        self.author = author
        self.language = language
        self.chapters: List[Tuple[str, str]] = []
        self.uid = f"urn:uuid:{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.headings: List[Tuple[int, str, str]] = []  # (level, text, id)
    
    def add_chapter(self, title: str, file_path: str) -> None:
        self.chapters.append((title, file_path))
    
    def generate(self, output_path: str) -> None:
        # Process chapters first to extract headings and images
        chapter_contents = []
        for i, (title, file_path) in enumerate(self.chapters, 1):
            html_content = self._process_file(file_path)
            chapter_contents.append((f'xhtml/chapter{i}.xhtml', html_content))
        
        with zipfile.ZipFile(output_path, 'w') as zf:
            # Add mimetype without compression (EPUB requirement)
            zf.writestr(zipfile.ZipInfo('mimetype'), 'application/epub+zip')
            
            # Create META-INF directory
            zf.writestr('META-INF/container.xml', self._generate_container_xml(), compress_type=zipfile.ZIP_DEFLATED)
            
            # Create OEBPS directories
            zf.writestr('OEBPS/styles/style.css', self._generate_style_css(), compress_type=zipfile.ZIP_DEFLATED)
            
            # Add default fonts
            self._add_default_fonts(zf)
            
            # Generate and add cover image
            self._generate_cover(zf)
            
            # Download and add images
            if hasattr(self, 'images'):
                for src, filename in self.images:
                    try:
                        # Check if it's a remote image
                        if src.startswith('http://') or src.startswith('https://'):
                            # Download the image
                            response = requests.get(src, timeout=10)
                            response.raise_for_status()
                            # Add to EPUB
                            zf.writestr(f'OEBPS/images/{filename}', response.content, compress_type=zipfile.ZIP_DEFLATED)
                            print(f"Successfully downloaded and added image: {src} -> images/{filename}")
                        else:
                            # Local image
                            # Read the image file
                            with open(src, 'rb') as f:
                                image_content = f.read()
                            # Add to EPUB
                            zf.writestr(f'OEBPS/images/{filename}', image_content, compress_type=zipfile.ZIP_DEFLATED)
                            print(f"Successfully added local image: {src} -> images/{filename}")
                    except Exception as e:
                        print(f"Error processing image {src}: {e}")
            
            # Add content files
            zf.writestr('OEBPS/content.opf', self._generate_content_opf(), compress_type=zipfile.ZIP_DEFLATED)
            zf.writestr('OEBPS/toc.ncx', self._generate_toc_ncx(), compress_type=zipfile.ZIP_DEFLATED)
            zf.writestr('OEBPS/nav.xhtml', self._generate_nav_xhtml(), compress_type=zipfile.ZIP_DEFLATED)
            
            # Add chapters
            for filename, content in chapter_contents:
                zf.writestr(f'OEBPS/{filename}', content, compress_type=zipfile.ZIP_DEFLATED)
    
    def _add_default_fonts(self, zf):
        """Add default fonts to the EPUB"""
        # Add font directory placeholder
        zf.writestr('OEBPS/fonts/.gitkeep', '')
    
    def _generate_cover(self, zf):
        """Generate a cover image using Pillow"""
        # Create cover image
        width, height = 1200, 1800
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Try to load a font, fallback to default if not available
        try:
            title_font = ImageFont.truetype('arial.ttf', 80)
            author_font = ImageFont.truetype('arial.ttf', 40)
        except IOError:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
        
        # Calculate text position
        title_bbox = draw.textbbox((0, 0), self.title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (width - title_width) // 2
        title_y = height // 3
        
        author_bbox = draw.textbbox((0, 0), f"by {self.author}", font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (width - author_width) // 2
        author_y = title_y + title_height + 50
        
        # Draw text
        draw.text((title_x, title_y), self.title, font=title_font, fill=(0, 0, 0))
        draw.text((author_x, author_y), f"by {self.author}", font=author_font, fill=(50, 50, 50))
        
        # Save cover image to a temporary file
        import io
        cover_buffer = io.BytesIO()
        image.save(cover_buffer, format='JPEG')
        cover_buffer.seek(0)
        
        # Add cover to EPUB
        zf.writestr('OEBPS/images/cover.jpg', cover_buffer.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
        print("Successfully generated and added cover image")
    
    def _generate_style_css(self) -> str:
        return '''/* Professional EPUB styles based on example.epub */

/* Font definitions */
@font-face {
    font-family: "Times New Roman";
    src: url(../fonts/times.ttf);
    font-style: normal;
    font-weight: normal;
}

@font-face {
    font-family: "Times New Roman";
    src: url(../fonts/timesbd.ttf);
    font-style: normal;
    font-weight: bold;
}

@font-face {
    font-family: "Times New Roman";
    src: url(../fonts/timesbi.ttf);
    font-style: italic;
    font-weight: bold;
}

@font-face {
    font-family: "Times New Roman";
    src: url(../fonts/timesi.ttf);
    font-style: italic;
    font-weight: normal;
}

:root {
    --color-background-page: #ffffff;
    --color-background-secondary: #f6f9fc;
    --color-text-primary: #333333;
    --color-text-secondary: #666666;
    --color-border-primary: #eaecef;
    --color-border-secondary: #dfe2e5;
    --color-blue-50: #0366d6;
    --color-blue-60: #005cc5;
    --color-green-50: #28a745;
    --color-red-50: #d73a49;
    --font-family-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-family-serif: "Times New Roman", serif;
    --font-family-code: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    --font-line-ui: 1.5;
    --radius-full: 9999px;
    --radius-sm: 0.25rem;
    --radius-md: 0.375rem;
}

body {
    font-family: var(--font-family-serif);
    line-height: 1.6;
    color: var(--color-text-primary);
    margin: 0;
    padding: 20px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    background-color: var(--color-background-page);
    text-align: justify;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-serif);
    font-weight: bold;
    margin-top: 2.5em;
    margin-bottom: 1.5em;
    color: var(--color-text-primary);
    line-height: 1.25;
}

h1 {
    font-size: 250%;
    text-align: center;
    margin-top: 3em;
    margin-bottom: 2.5em;
}

h2 {
    font-size: 200%;
    text-align: center;
    margin-top: 2.5em;
    margin-bottom: 2em;
}

h3 {
    font-size: 150%;
    margin-top: 2.2em;
    margin-bottom: 1.5em;
}

h4 {
    font-size: 125%;
    margin-top: 2em;
    margin-bottom: 1.2em;
}

h5 {
    font-size: 110%;
    margin-top: 1.8em;
    margin-bottom: 1em;
}

h6 {
    font-size: 100%;
    color: var(--color-text-secondary);
    margin-top: 1.6em;
    margin-bottom: 0.8em;
}

p {
    margin-bottom: 1.5em;
    text-align: justify;
    margin-top: 1em;
}

.noindent {
    margin-top: 2.3em;
    margin-bottom: 0.2em;
    text-align: justify;
}

.indenthanging {
    margin-top: 0.2em;
    font-size: 90%;
    margin-left: 1.8em;
    text-indent: -1.8em;
    margin-bottom: 0.1em;
    text-align: justify;
}

ul, ol {
    margin-bottom: 1.5em;
    padding-left: 2em;
    margin-top: 1em;
    list-style: disc;
}

ol {
    list-style: decimal;
}

li {
    margin-bottom: 0.5em;
    text-align: justify;
}

li > ul,
li > ol {
    margin-top: 0.5em;
    margin-bottom: 0;
}

code {
    font-family: var(--font-family-code);
    background-color: var(--color-background-secondary);
    color: var(--color-red-50);
    padding: 0.2em 0.4em;
    border-radius: var(--radius-sm);
    font-size: 0.9em;
}

pre {
    background-color: var(--color-background-secondary);
    border: 1px solid var(--color-border-primary);
    border-radius: var(--radius-md);
    overflow-x: auto;
    margin-bottom: 1.5em;
    margin-top: 1.5em;
    padding: 0;
}

pre code {
    background-color: #f8f9fa;
    padding: 1em;
    color: var(--color-text-primary);
    display: block;
    white-space: pre-wrap;
}

.code-example {
    border: 1px solid var(--color-border-primary);
    border-radius: var(--radius-md);
    overflow: hidden;
    margin-bottom: 1.5em;
    margin-top: 1.5em;
}

.code-example pre {
    margin: 0;
    border: none;
    border-radius: 0;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 2.5em auto;
    border-radius: var(--radius-md);
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1.5em;
    margin-top: 1.5em;
    font-size: 0.9em;
}

table, th, td {
    border: 1px solid var(--color-border-primary);
}

th, td {
    padding: 0.75em;
    text-align: left;
}

th {
    background-color: var(--color-background-secondary);
    font-weight: bold;
    color: var(--color-text-primary);
}

tr:nth-child(even) {
    background-color: var(--color-background-secondary);
}

a {
    font-family: var(--font-family-sans);
    color: var(--color-blue-50);
    text-decoration: underline;
}

a:hover {
    text-decoration: underline;
    color: var(--color-blue-60);
}

blockquote {
    border-left: 4px solid var(--color-border-primary);
    padding-left: 1em;
    margin-left: 0;
    margin-right: 0;
    color: var(--color-text-secondary);
    font-style: italic;
    margin-bottom: 1.5em;
    margin-top: 1.5em;
}

hr {
    border: 0;
    border-top: 1px solid var(--color-border-primary);
    margin: 2.5em 0;
}

small {
    font-size: 80%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    body {
        padding: 15px;
    }
    
    h1 {
        font-size: 200%;
        margin-top: 2em;
        margin-bottom: 2em;
    }
    
    h2 {
        font-size: 175%;
    }
    
    h3 {
        font-size: 125%;
    }
}
'''
    
    def _generate_content_opf(self) -> str:
        # Create the content.opf file manually to ensure all elements are included
        parts = []
        parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        parts.append('<package xmlns="http://www.idpf.org/2007/opf" version="3.3" unique-identifier="bookid">')
        parts.append('  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">')
        parts.append('    <dc:title>%s</dc:title>' % self.title)
        parts.append('    <dc:creator opf:role="aut">%s</dc:creator>' % self.author)
        parts.append('    <dc:language>%s</dc:language>' % self.language)
        parts.append('    <dc:identifier id="bookid">%s</dc:identifier>' % self.uid)
        parts.append('    <dc:date>%s</dc:date>' % datetime.now().strftime('%Y-%m-%d'))
        parts.append('    <meta property="dcterms:modified">%s</meta>' % self.timestamp)
        parts.append('    <meta name="cover" content="cover-image"/>')
        parts.append('  </metadata>')
        parts.append('  <manifest>')
        parts.append('    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
        parts.append('    <item id="ncxtoc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
        parts.append('    <item id="style" href="styles/style.css" media-type="text/css"/>')
        parts.append('    <item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>')
        
        # Add image items
        if hasattr(self, 'images'):
            for i, (src, filename) in enumerate(self.images):
                # Determine media type based on file extension
                ext = filename.split('.')[-1].lower()
                media_type = 'image/jpeg'  # Default
                if ext in ['png']:
                    media_type = 'image/png'
                elif ext in ['gif']:
                    media_type = 'image/gif'
                elif ext in ['svg']:
                    media_type = 'image/svg+xml'
                parts.append('    <item id="image%d" href="images/%s" media-type="%s"/>' % (i+1, filename, media_type))
        
        # Add chapter items
        for i in range(len(self.chapters)):
            parts.append('    <item id="chapter%d" href="xhtml/chapter%d.xhtml" media-type="application/xhtml+xml"/>' % (i+1, i+1))
        
        # Add spine
        parts.append('  </manifest>')
        parts.append('  <spine toc="ncxtoc">')
        
        # Add itemrefs
        for i in range(len(self.chapters)):
            parts.append('    <itemref idref="chapter%d"/>' % (i+1))
        
        parts.append('  </spine>')
        parts.append('</package>')
        
        return '\n'.join(parts)
    
    def _generate_container_xml(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
    
    def _generate_nav_xhtml(self) -> str:
        # Create a simple flat list for now to ensure correct HTML structure
        html = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>{self.title}</title>
    <meta charset="UTF-8"/>
    <link rel="stylesheet" href="styles/style.css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h1>{self.title}</h1>
        <ol>
'''
        
        # Check if we have extracted headings
        if hasattr(self, 'headings') and self.headings:
            # Generate table of contents from headings
            for level, text, heading_id in self.headings:
                # Indent based on heading level
                indent = '            ' + '  ' * (level - 1)
                html += f'{indent}<li><a href="xhtml/chapter1.xhtml#{heading_id}">{text}</a></li>\n'
        else:
            # Fall back to chapter titles
            for i, (title, _) in enumerate(self.chapters, 1):
                html += f'            <li><a href="xhtml/chapter{i}.xhtml">{title}</a></li>\n'
        
        html += '''        </ol>
    </nav>
</body>
</html>'''
        
        return html
    
    def _generate_toc_ncx(self) -> str:
        root = ET.Element('ncx', {
            'xmlns': 'http://www.daisy.org/z3986/2005/ncx/',
            'version': '2005-1'
        })
        
        # Head
        head = ET.SubElement(root, 'head')
        ET.SubElement(head, 'meta', {'name': 'dtb:uid', 'content': self.uid})
        ET.SubElement(head, 'meta', {'name': 'dtb:depth', 'content': '1'})
        ET.SubElement(head, 'meta', {'name': 'dtb:totalPageCount', 'content': '0'})
        ET.SubElement(head, 'meta', {'name': 'dtb:maxPageNumber', 'content': '0'})
        
        # DocTitle
        doc_title = ET.SubElement(root, 'docTitle')
        ET.SubElement(doc_title, 'text').text = self.title
        
        # DocAuthor
        doc_author = ET.SubElement(root, 'docAuthor')
        ET.SubElement(doc_author, 'text').text = self.author
        
        # NavMap
        nav_map = ET.SubElement(root, 'navMap')
        
        # Check if we have extracted headings
        if hasattr(self, 'headings') and self.headings:
            # Generate table of contents from headings
            for i, (level, text, heading_id) in enumerate(self.headings, 1):
                nav_point = ET.SubElement(nav_map, 'navPoint', {
                    'id': heading_id,
                    'playOrder': str(i)
                })
                nav_label = ET.SubElement(nav_point, 'navLabel')
                ET.SubElement(nav_label, 'text').text = text
                ET.SubElement(nav_point, 'content', {'src': f'xhtml/chapter1.xhtml#{heading_id}'})
        else:
            # Fall back to chapter titles
            for i, (title, _) in enumerate(self.chapters, 1):
                nav_point = ET.SubElement(nav_map, 'navPoint', {
                    'id': f'chapter{i}',
                    'playOrder': str(i)
                })
                nav_label = ET.SubElement(nav_point, 'navLabel')
                ET.SubElement(nav_label, 'text').text = title
                ET.SubElement(nav_point, 'content', {'src': f'xhtml/chapter{i}.xhtml'})
        
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    def _process_file(self, file_path: str) -> str:
        raise NotImplementedError("Subclasses must implement _process_file method")
    
    def _wrap_html(self, content: str) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8"/>
    <link rel="stylesheet" href="../styles/style.css"/>
</head>
<body>
{content}
</body>
</html>'''