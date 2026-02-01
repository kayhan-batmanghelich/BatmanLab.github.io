#!/usr/bin/env python3
"""
Correctly download ALL images and link them to CORRESPONDING publications
"""

import json
import re
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def download_image(url, save_path):
    """Download an image from URL to save_path."""
    try:
        if url.startswith('hhttps'):
            url = url[1:]
        
        if not url or url == "":
            return None
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        if path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            ext = os.path.splitext(path)[1]
        else:
            ext = '.png'
        
        if not save_path.endswith(ext):
            save_path = os.path.splitext(save_path)[0] + ext
        
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urlopen(req, timeout=30) as response:
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type and not save_path.endswith('.jpg'):
                save_path = os.path.splitext(save_path)[0] + '.jpg'
            
            with open(save_path, 'wb') as f:
                f.write(response.read())
        
        print(f"✓ Downloaded: {os.path.basename(save_path)}")
        return save_path
    except (URLError, HTTPError, Exception) as e:
        print(f"✗ Failed: {url[:60] if url else 'empty'}...: {e}")
        return None

def sanitize_filename(title):
    """Create a safe filename from paper title."""
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:80]

def update_image_for_paper(html_content, title, image_path):
    """Update image src for a specific paper by finding the h5 tag with the title."""
    # Escape title for regex
    escaped_title = re.escape(title)
    # Handle HTML entities
    escaped_title = escaped_title.replace(r'\&', r'(&amp;|&)')
    
    # Find the article that contains an h5 with this exact title
    # Pattern: <article>...<img src="CURRENT">...<h5>TITLE</h5>...</article>
    # We'll match from article start to h5, then replace the img src
    pattern = rf'(<article class="item-row">\s*<img src=")[^"]+(" alt="[^"]*" onerror="[^"]*">\s*<div>\s*<h5[^>]*>{escaped_title}</h5>)'
    
    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    if match:
        # Replace the img src
        new_content = html_content[:match.start()] + match.group(1) + image_path + match.group(2) + html_content[match.end():]
        print(f"✓ Linked: {title[:55]}...")
        return new_content, True
    else:
        print(f"⚠ Not found: {title[:55]}...")
        return html_content, False

def main():
    base_dir = Path(__file__).parent
    index_html_path = base_dir / "index.html"
    images_dir = base_dir / "images" / "publications"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Load JSON
    json_file = base_dir / "publications_complete.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded JSON: {sum(len(pubs) for pubs in data.values())} publications")
    
    # Read HTML
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n" + "=" * 60)
    print("Downloading images and linking to publications...")
    print("=" * 60)
    
    downloaded = 0
    linked = 0
    failed = 0
    no_url = 0
    
    # Process all papers
    for year in sorted(data.keys(), reverse=True):
        papers = data[year]
        for idx, paper in enumerate(papers, 1):
            title = paper.get("title", "")
            img_url = paper.get("image_icon_link", "")
            
            if not title:
                continue
            
            if not img_url or img_url == "":
                # Use placeholder
                html_content, updated = update_image_for_paper(html_content, title, "images/bu-logo.png")
                if updated:
                    no_url += 1
                continue
            
            # Create filename
            safe_title = sanitize_filename(title)
            if img_url.endswith(('.jpg', '.jpeg')):
                img_filename = f"{year}_{idx:02d}_{safe_title}.jpg"
            else:
                img_filename = f"{year}_{idx:02d}_{safe_title}.png"
            
            img_path = images_dir / img_filename
            relative_path = f"images/publications/{img_filename}"
            
            # Download
            downloaded_path = download_image(img_url, str(img_path))
            if downloaded_path:
                downloaded += 1
                img_path = Path(downloaded_path)
                relative_path = f"images/publications/{img_path.name}"
                
                # Link to HTML
                html_content, updated = update_image_for_paper(html_content, title, relative_path)
                if updated:
                    linked += 1
            else:
                failed += 1
                # Use placeholder for failed downloads
                html_content, updated = update_image_for_paper(html_content, title, "images/bu-logo.png")
                if updated:
                    no_url += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary: {downloaded} downloaded, {linked} linked, {no_url} placeholders, {failed} failed")
    print(f"{'=' * 60}")
    
    # Write HTML
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Updated index.html")

if __name__ == "__main__":
    main()
