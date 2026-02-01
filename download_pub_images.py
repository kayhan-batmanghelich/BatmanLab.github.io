#!/usr/bin/env python3
"""
Download publication images from JSON file.
Usage: python3 download_pub_images.py <json_file>
"""

import json
import urllib.request
import sys
from pathlib import Path

def download_image(url, filename):
    """Download image from URL exactly as provided"""
    if not url or url == "":
        return False
    try:
        # Use URL exactly as provided - don't decode/encode it
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                with open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"✓ Downloaded: {filename}")
                return True
            else:
                print(f"✗ HTTP {response.status} for {filename}")
                return False
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP {e.code} for {url[:80]}...")
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__} for {url[:80]}...")
        return False

def main():
    # Create images directory
    images_dir = Path("images/publications")
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Read JSON from file or stdin
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("Reading JSON from stdin...")
        data = json.load(sys.stdin)
    
    # Flatten all publications in order (2025, 2024, 2023, ...)
    all_pubs = []
    for year in sorted(data.keys(), reverse=True):
        for pub in data[year]:
            all_pubs.append((year, pub))
    
    # Download images with sequential numbering matching HTML
    downloaded = 0
    failed = 0
    skipped = 0
    
    for seq_num, (year, pub) in enumerate(all_pubs, start=1):
        img_url = pub.get("image_icon_link", "")
        if img_url:
            # Determine file extension
            if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                img_filename = f"pub_{year}_{seq_num}.jpg"
            else:
                img_filename = f"pub_{year}_{seq_num}.png"
            
            img_path = images_dir / img_filename
            
            if img_path.exists():
                print(f"⊘ Already exists: {img_filename}")
                skipped += 1
            else:
                if download_image(img_url, str(img_path)):
                    downloaded += 1
                else:
                    failed += 1
        else:
            skipped += 1
    
    print(f"\n{'='*60}")
    print(f"Summary: {downloaded} downloaded, {failed} failed, {skipped} skipped, {len(all_pubs)} total")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
