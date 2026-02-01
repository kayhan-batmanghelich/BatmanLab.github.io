#!/usr/bin/env python3
"""
Download ALL image icons from JSON and link them to CORRESPONDING publications in index.html
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
        # Fix URL if it has double 'h'
        if url.startswith('hhttps'):
            url = url[1:]
        
        if not url or url == "":
            return None
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Determine file extension from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        if path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            ext = os.path.splitext(path)[1]
        else:
            ext = '.png'
        
        # Update save_path with correct extension
        if not save_path.endswith(ext):
            save_path = os.path.splitext(save_path)[0] + ext
        
        # Download with urllib
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
        print(f"✗ Failed to download {url[:60] if url else 'empty URL'}...: {e}")
        return None

def sanitize_filename(title):
    """Create a safe filename from paper title."""
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:80]

def find_paper_article_block(html_content, title):
    """Find the article block for a paper by matching title in h5 tag."""
    # Escape special regex characters but allow flexible matching
    escaped_title = re.escape(title)
    # Match article block containing this exact title in h5
    pattern = rf'(<article class="item-row">.*?<h5[^>]*>{escaped_title}</h5>.*?</article>)'
    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    return match

def update_image_src(html_content, title, image_path):
    """Update the image src for a specific paper by title."""
    # Escape the title for regex, but handle HTML entities
    escaped_title = re.escape(title)
    # Handle HTML-escaped ampersand
    escaped_title = escaped_title.replace(r'\&', r'(&amp;|&)')
    
    # Find the article block by matching the h5 tag with the title
    # The structure is: <article><img src="..."><div><h5>title</h5>...
    # We need to find the img tag in the same article as the h5 with this title
    pattern = rf'(<article class="item-row">\s*<img src=")[^"]+(" alt="[^"]*" onerror="[^"]*">\s*<div>\s*<h5[^>]*>{escaped_title}</h5>)'
    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        # Try a more flexible pattern - match any img before the h5 with this title in the same article
        pattern2 = rf'(<article class="item-row">.*?<img src=")[^"]+(" alt="[^"]*" onerror="[^"]*">.*?<h5[^>]*>{escaped_title}</h5>)'
        match = re.search(pattern2, html_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        print(f"⚠ Could not find paper in HTML: {title[:60]}...")
        return html_content, False
    
    # Replace the img src
    updated_content = html_content[:match.start()] + match.group(1) + image_path + match.group(2) + html_content[match.end():]
    print(f"✓ Linked image for: {title[:60]}...")
    return updated_content, True

def main():
    base_dir = Path(__file__).parent
    index_html_path = base_dir / "index.html"
    images_dir = base_dir / "images" / "publications"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Load JSON
    json_file = base_dir / "publications_complete.json"
    if not json_file.exists():
        print(f"✗ JSON file not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        full_json_data = json.load(f)
    
    print(f"✓ Loaded JSON with {sum(len(pubs) for pubs in full_json_data.values())} publications")
    
    # Read HTML
    print(f"\nReading {index_html_path}...")
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n" + "=" * 60)
    print("Downloading ALL image icons and linking to publications...")
    print("=" * 60)
    
    downloaded_count = 0
    linked_count = 0
    failed_count = 0
    no_image_count = 0
    
    # Process all papers from JSON in reverse chronological order
    for year in sorted(full_json_data.keys(), reverse=True):
        papers = full_json_data[year]
        for idx, paper in enumerate(papers, 1):
            title = paper.get("title", "")
            img_url = paper.get("image_icon_link", "")
            
            if not title:
                continue
            
            if not img_url or img_url == "":
                # Use placeholder for papers without image URLs
                relative_path = "images/bu-logo.png"
                html_content, updated = update_image_src(html_content, title, relative_path)
                if updated:
                    no_image_count += 1
                continue
            
            # Create filename: YEAR_NN_Title.ext
            safe_title = sanitize_filename(title)
            if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                img_filename = f"{year}_{idx:02d}_{safe_title}.jpg"
            else:
                img_filename = f"{year}_{idx:02d}_{safe_title}.png"
            
            img_path = images_dir / img_filename
            relative_path = f"images/publications/{img_filename}"
            
            # Download image
            downloaded_path = download_image(img_url, str(img_path))
            if downloaded_path:
                downloaded_count += 1
                # Update path to use actual downloaded filename
                img_path = Path(downloaded_path)
                relative_path = f"images/publications/{img_path.name}"
                
                # Link to corresponding publication in HTML
                html_content, updated = update_image_src(html_content, title, relative_path)
                if updated:
                    linked_count += 1
            else:
                failed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Downloaded: {downloaded_count} images")
    print(f"  Linked to HTML: {linked_count} papers")
    print(f"  No image URL (placeholder): {no_image_count} papers")
    print(f"  Failed downloads: {failed_count}")
    print(f"{'=' * 60}")
    
    # Write updated HTML
    print(f"\nWriting updated HTML to {index_html_path}...")
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Successfully updated index.html")

if __name__ == "__main__":
    main()
