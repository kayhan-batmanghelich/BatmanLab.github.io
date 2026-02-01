#!/usr/bin/env python3
"""
Complete script to update publications:
1. Download image icons for specified papers
2. Update code links for ALL papers from JSON
"""

import json
import re
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Papers that need image icons downloaded
PAPERS_TO_UPDATE_IMAGES = [
    "Mammo-CLIP: A Vision Language Foundation Model to Enhance Data Efficiency and Robustness in Mammography",
    "Anatomy-specific Progression Classification in Chest Radiographs via Weakly Supervised Learning",
    "Beyond Distribution Shift: Spurious Features Through the Lens of Training Dynamics",
    "Automated Detection of Premalignant Oral Lesions on Whole Slide Images Using CNN",
    "Anatomy-Guided Weakly-Supervised Abnormality Localization in Chest X-rays",
    "Adversarial Consistency for Single Domain Generalization in Medical Image Segmentation",
    "Hierarchical Amortized Training for Memory-efficient High-Resolution 3D GAN",
    "Maximum Spatial Perturbation Consistency for Unpaired Image-to-Image Translation",
    "Knowledge Distillation via Constrained Variational Inference"
]

def download_image(url, save_path):
    """Download an image from URL to save_path."""
    try:
        # Fix URL if it has double 'h' (like in Anatomy-Guided)
        if url.startswith('hhttps'):
            url = url[1:]
        
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
        print(f"✗ Failed to download {url[:60]}...: {e}")
        return None

def sanitize_filename(title):
    """Create a safe filename from paper title."""
    # Remove special characters and limit length
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:80]  # Limit length

def find_paper_in_html(html_content, title):
    """Find the article block for a paper by title."""
    # Escape special regex characters in title, but allow flexible matching
    # The title in HTML might have slight variations
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
        return html_content
    
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
    return html_content

def update_code_link_in_html(html_content, title, code_link):
    """Update or add code link for a paper."""
    if not code_link:
        return html_content
    
    # Find the article block
    match = find_paper_in_html(html_content, title)
    if not match:
        print(f"⚠ Could not find paper for code link: {title[:60]}...")
        return html_content
    
    article_block = match.group(1)
    
    # Check if code link already exists
    code_link_pattern = r'<a href="[^"]*"><i class="bi bi-github"></i> Code</a>'
    code_link_html = f'<a href="{code_link}"><i class="bi bi-github"></i> Code</a>'
    
    if re.search(code_link_pattern, article_block):
        # Update existing code link
        updated_block = re.sub(
            r'(<a href=")[^"]*("<i class="bi bi-github"></i> Code</a>)',
            rf'\1{code_link}\2',
            article_block
        )
    else:
        # Add code link to meta-links div
        if '<div class="meta-links mb-2">' in article_block:
            # Add code link to existing meta-links
            updated_block = re.sub(
                r'(<div class="meta-links mb-2">)(.*?)(</div>)',
                rf'\1\2 {code_link_html}\3',
                article_block
            )
        else:
            # Create meta-links div if it doesn't exist
            # Try to find venue div and add after it
            if '<div class="mb-1"><span class="fw-semibold">Venue:</span>' in article_block:
                updated_block = re.sub(
                    r'(<div class="mb-1"><span class="fw-semibold">Venue:</span>[^<]*</div>)',
                    rf'\1\n                    <div class="meta-links mb-2">{code_link_html}</div>',
                    article_block
                )
            else:
                # Add before closing div
                updated_block = re.sub(
                    r'(</div>\s*</div>\s*</article>)',
                    rf'                    <div class="meta-links mb-2">{code_link_html}</div>\n                </div>\n            </article>',
                    article_block
                )
    
    # Replace in full HTML
    html_content = html_content[:match.start()] + updated_block + html_content[match.end():]
    print(f"✓ Updated code link for: {title[:60]}...")
    return html_content

def main():
    base_dir = Path(__file__).parent
    index_html_path = base_dir / "index.html"
    images_dir = base_dir / "images" / "publications"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to load JSON from various possible files
    json_files = [
        base_dir / "publications_complete.json",
        base_dir / "publications_full.json",
        base_dir / "publications_data.json",
        base_dir / "publications_new.json",
        base_dir / "publications_user_data.json"
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
        print("✗ No valid JSON file found. Please ensure publications_full.json exists.")
        return
    
    # Read HTML
    print(f"\nReading {index_html_path}...")
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Step 1: Download images for specified papers
    print("\n" + "=" * 60)
    print("Step 1: Downloading images for specified papers...")
    print("=" * 60)
    
    # Create a mapping of title -> paper data
    title_to_paper = {}
    for year, papers in full_json_data.items():
        for paper in papers:
            title = paper.get("title", "")
            if title:
                title_to_paper[title] = paper
    
    # Download images and update HTML
    downloaded_count = 0
    for title in PAPERS_TO_UPDATE_IMAGES:
        if title in title_to_paper:
            paper = title_to_paper[title]
            img_url = paper.get("image_icon_link", "")
            
            if not img_url:
                print(f"⚠ No image URL for: {title[:60]}...")
                continue
            
            # Create filename based on existing naming convention
            # Use year and a sanitized version of title
            year = None
            for y, papers in full_json_data.items():
                if paper in papers:
                    year = y
                    break
            
            # Find the index in that year
            if year:
                idx = full_json_data[year].index(paper) + 1
                # Use similar naming to existing files: YEAR_NN_Title.png
                safe_title = sanitize_filename(title)
                if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                    img_filename = f"{year}_{idx:02d}_{safe_title}.jpg"
                else:
                    img_filename = f"{year}_{idx:02d}_{safe_title}.png"
            else:
                safe_title = sanitize_filename(title)
                if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                    img_filename = f"{safe_title}.jpg"
                else:
                    img_filename = f"{safe_title}.png"
            
            img_path = images_dir / img_filename
            relative_path = f"images/publications/{img_filename}"
            
            # Download if not exists
            if not img_path.exists():
                downloaded_path = download_image(img_url, str(img_path))
                if downloaded_path:
                    downloaded_count += 1
                    # Update path to use downloaded filename
                    img_path = Path(downloaded_path)
                    relative_path = f"images/publications/{img_path.name}"
            else:
                print(f"✓ Image already exists: {img_filename}")
            
            # Update HTML
            html_content = update_image_in_html(html_content, title, relative_path)
        else:
            print(f"⚠ Paper not found in JSON: {title[:60]}...")
    
    print(f"\nDownloaded {downloaded_count} new images")
    
    # Step 2: Update code links for ALL papers
    print("\n" + "=" * 60)
    print("Step 2: Updating code links for all papers...")
    print("=" * 60)
    
    updated_code_count = 0
    for year, papers in full_json_data.items():
        for paper in papers:
            title = paper.get("title", "")
            code_link = paper.get("code_link")
            
            if title and code_link:
                old_content = html_content
                html_content = update_code_link_in_html(html_content, title, code_link)
                if html_content != old_content:
                    updated_code_count += 1
    
    print(f"\nUpdated {updated_code_count} code links")
    
    # Write updated HTML
    print(f"\nWriting updated HTML to {index_html_path}...")
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("✓ Successfully updated index.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
