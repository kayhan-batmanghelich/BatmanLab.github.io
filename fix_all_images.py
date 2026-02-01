#!/usr/bin/env python3
"""
Script to download ALL image icons from JSON and link them correctly in index.html
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
        # Fix URL if it has double 'h' (like in Anatomy-Guided)
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
            # Update extension based on content type if needed
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
    # Remove special characters and limit length
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:80]  # Limit length

def find_paper_in_html(html_content, title):
    """Find the article block for a paper by title."""
    # Escape special regex characters in title
    escaped_title = re.escape(title)
    # Match the article block containing this title (case insensitive)
    pattern = rf'(<article class="item-row">.*?<h5[^>]*>{escaped_title}</h5>.*?</article>)'
    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
    return match

def update_image_in_html(html_content, title, image_path):
    """Update the image src for a paper."""
    # Find the article block
    match = find_paper_in_html(html_content, title)
    if not match:
        print(f"⚠ Could not find paper: {title[:60]}...")
        return html_content, False
    
    article_block = match.group(1)
    # Update the img src attribute
    updated_block = re.sub(
        r'(<img src=")[^"]+(" alt="[^"]*" onerror="[^"]*")',
        rf'\1{image_path}\2',
        article_block
    )
    
    # Replace in full HTML
    html_content = html_content[:match.start()] + updated_block + html_content[match.end():]
    print(f"✓ Updated image for: {title[:60]}...")
    return html_content, True

def main():
    base_dir = Path(__file__).parent
    index_html_path = base_dir / "index.html"
    images_dir = base_dir / "images" / "publications"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load JSON from various possible files
    json_files = [
        base_dir / "publications_complete.json",
        base_dir / "publications_user_data.json",
        base_dir / "publications_full.json",
        base_dir / "publications_data.json",
    ]
    
    full_json_data = None
    for json_file in json_files:
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    full_json_data = json.load(f)
                print(f"✓ Loaded JSON from {json_file.name}")
                break
            except Exception as e:
                print(f"⚠ Error loading {json_file.name}: {e}")
                continue
    
    if not full_json_data:
        print("✗ No valid JSON file found.")
        return
    
    # Read HTML
    print(f"\nReading {index_html_path}...")
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("\n" + "=" * 60)
    print("Downloading ALL image icons from JSON...")
    print("=" * 60)
    
    # Process all papers from JSON
    downloaded_count = 0
    updated_count = 0
    failed_count = 0
    
    for year in sorted(full_json_data.keys(), reverse=True):
        papers = full_json_data[year]
        for idx, paper in enumerate(papers, 1):
            title = paper.get("title", "")
            img_url = paper.get("image_icon_link", "")
            
            if not title:
                continue
            
            if not img_url or img_url == "":
                print(f"⚠ No image URL for: {title[:60]}... (will use placeholder)")
                # Use placeholder image for papers without image URLs
                relative_path = "images/bu-logo.png"
                html_content, updated = update_image_in_html(html_content, title, relative_path)
                if updated:
                    updated_count += 1
                continue
            
            # Create filename: YEAR_NN_Title.png
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
                # Update path to use downloaded filename
                img_path = Path(downloaded_path)
                relative_path = f"images/publications/{img_path.name}"
                
                # Update HTML
                html_content, updated = update_image_in_html(html_content, title, relative_path)
                if updated:
                    updated_count += 1
            else:
                failed_count += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Downloaded: {downloaded_count} images")
    print(f"  Updated in HTML: {updated_count} papers")
    print(f"  Failed: {failed_count} downloads")
    print(f"{'=' * 60}")
    
    # Write updated HTML
    print(f"\nWriting updated HTML to {index_html_path}...")
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✓ Successfully updated index.html")

if __name__ == "__main__":
    main()
