#!/usr/bin/env python3
"""
Script to download publication images and set up the publications folder structure.
"""

import json
import os
import urllib.request
import urllib.parse
from pathlib import Path
import re
from urllib.error import URLError, HTTPError

def sanitize_filename(title, year, index):
    """Create a safe filename from publication title."""
    # Take first 50 chars, remove special chars, replace spaces with underscores
    safe = re.sub(r'[^\w\s-]', '', title[:50])
    safe = re.sub(r'[-\s]+', '_', safe)
    return f"{year}_{index:02d}_{safe}.png"

def download_image(url, save_path):
    """Download an image from URL to save_path."""
    if not url or url == "":
        return False
    
    try:
        # Create a request with headers to avoid 403 errors
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=30) as response:
            # Determine file extension from URL or content type
            content_type = response.headers.get('Content-Type', '')
            ext = '.png'
            if 'jpeg' in content_type or 'jpg' in content_type or url.lower().endswith(('.jpg', '.jpeg')):
                ext = '.jpg'
            elif 'gif' in content_type or url.lower().endswith('.gif'):
                ext = '.gif'
            
            # Update save_path with correct extension
            if not save_path.endswith(ext):
                save_path = str(Path(save_path).with_suffix(ext))
            
            with open(save_path, 'wb') as f:
                f.write(response.read())
        
        return True
    except (URLError, HTTPError, Exception) as e:
        print(f"  Error downloading {url[:60]}...: {e}")
        return False

def main():
    # Paths
    base_dir = Path(__file__).parent
    images_dir = base_dir / "images"
    publications_dir = images_dir / "publications"
    json_file = base_dir / "publications_data.json"
    
    # Create publications directory
    publications_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created/verified publications directory: {publications_dir}")
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Track downloads
    downloaded = 0
    skipped = 0
    failed = 0
    image_mapping = {}  # Maps (year, index) to filename
    
    # Process each year
    for year in sorted(data.keys(), reverse=True):
        print(f"\nProcessing year {year}...")
        
        for idx, pub in enumerate(data[year], 1):
            title = pub.get("title", "")
            img_url = pub.get("image_icon_link", "")
            
            # Generate filename
            filename = sanitize_filename(title, year, idx)
            img_path = publications_dir / filename
            
            # Store mapping
            key = f"{year}_{idx}"
            image_mapping[key] = filename
            
            if not img_url or img_url == "":
                print(f"  [{idx}] No image URL for: {title[:50]}...")
                skipped += 1
                continue
            
            # Check if already exists
            if img_path.exists():
                print(f"  [{idx}] Already exists: {filename}")
                continue
            
            # Download image
            print(f"  [{idx}] Downloading: {title[:50]}...")
            if download_image(img_url, str(img_path)):
                downloaded += 1
                print(f"       ✓ Saved: {filename}")
            else:
                failed += 1
                # Try with .png extension
                png_path = publications_dir / f"{year}_{idx:02d}_default.png"
                if not png_path.exists():
                    print(f"       ✗ Failed, will use placeholder")
    
    # Save mapping to JSON for reference
    mapping_file = base_dir / "publication_image_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(image_mapping, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Downloaded: {downloaded}")
    print(f"  Skipped (no URL): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Total processed: {downloaded + skipped + failed}")
    print(f"\nImages saved to: {publications_dir}")
    print(f"Mapping saved to: {mapping_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
