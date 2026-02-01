#!/usr/bin/env python3
"""
Script to update publications in index.html:
1. Download image icons for specific papers
2. Update code links for all papers from JSON
"""

import json
import re
import os
import requests
from pathlib import Path
from urllib.parse import urlparse

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
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Determine file extension from URL or content type
        parsed_url = urlparse(url)
        path = parsed_url.path
        if path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            ext = os.path.splitext(path)[1]
        elif 'image/jpeg' in response.headers.get('content-type', ''):
            ext = '.jpg'
        else:
            ext = '.png'
        
        # Update save_path with correct extension
        if not save_path.endswith(ext):
            save_path = os.path.splitext(save_path)[0] + ext
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded: {os.path.basename(save_path)}")
        return save_path
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return None

def sanitize_filename(title):
    """Create a safe filename from paper title."""
    # Remove special characters and limit length
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:100]  # Limit length

def find_paper_in_html(html_content, title):
    """Find the article block for a paper by title."""
    # Escape special regex characters in title
    escaped_title = re.escape(title)
    # Match the article block containing this title
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
        # Add code link before closing div of meta-links
        # Find the meta-links div
        if '<div class="meta-links mb-2">' in article_block:
            # Add code link to meta-links
            updated_block = re.sub(
                r'(<div class="meta-links mb-2">)(.*?)(</div>)',
                rf'\1\2 {code_link_html}\3',
                article_block
            )
        else:
            # Create meta-links div if it doesn't exist
            # Find where to insert (before closing div of article content)
            updated_block = re.sub(
                r'(<div class="mb-1"><span class="fw-semibold">Venue:</span>[^<]*</div>)',
                rf'\1\n                    <div class="meta-links mb-2">{code_link_html}</div>',
                article_block
            )
    
    # Replace in full HTML
    html_content = html_content[:match.start()] + updated_block + html_content[match.end():]
    print(f"✓ Updated code link for: {title[:60]}...")
    return html_content

def main():
    # Load JSON data
    json_data = {
        "2024": [
            {
                "title": "MedSyn: Text-guided Anatomy-aware Synthesis of High-Fidelity 3D CT Images",
                "code_link": "https://github.com/batmanlab/MedSyn",
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.39.24%E2%80%AFPM-600x178.png"
            },
            {
                "title": "Mammo-CLIP: A Vision Language Foundation Model to Enhance Data Efficiency and Robustness in Mammography",
                "code_link": "https://github.com/batmanlab/Mammo-CLIP",
                "image_icon_link": "https://batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.59.40%E2%80%AFPM-600x230.png"
            },
            {
                "title": "Anatomy-specific Progression Classification in Chest Radiographs via Weakly Supervised Learning",
                "code_link": None,
                "image_icon_link": "https://batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.43.25%E2%80%AFPM-600x435.png"
            }
        ],
        "2023": [
            {
                "title": "Beyond Distribution Shift: Spurious Features Through the Lens of Training Dynamics",
                "code_link": "https://github.com/batmanlab/SpuriousFeaturesTrainingDynamics",
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/kmnist_expts-300x161.jpg"
            }
        ],
        "2022": [
            {
                "title": "Automated Detection of Premalignant Oral Lesions on Whole Slide Images Using CNN",
                "code_link": None,
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/11/Screenshot-2022-11-06-at-8.42.48-PM-600x144.png"
            },
            {
                "title": "Anatomy-Guided Weakly-Supervised Abnormality Localization in Chest X-rays",
                "code_link": "https://github.com/batmanlab/AGXNet",
                "image_icon_link": "hhttps://www.batman-lab.com/wp-content/uploads/2022/10/Screen-Shot-2022-10-13-at-12.08.02-AM-600x420.png"
            },
            {
                "title": "Adversarial Consistency for Single Domain Generalization in Medical Image Segmentation",
                "code_link": "https://github.com/batmanlab/Adversarial-Single-Domain-Generalization",
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/10/Screen-Shot-2022-10-12-at-11.38.41-PM-600x384.png"
            },
            {
                "title": "Hierarchical Amortized Training for Memory-efficient High-Resolution 3D GAN",
                "code_link": "https://github.com/batmanlab/HierarchicalAmortized3DGAN",
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2020/09/Screen-Shot-2020-09-16-at-7.53.39-PM-600x551.png"
            },
            {
                "title": "Maximum Spatial Perturbation Consistency for Unpaired Image-to-Image Translation",
                "code_link": "https://github.com/batmanlab/MaxSpatialPerturbationConsistency",
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/03/Yanwu_CVPR22.png"
            },
            {
                "title": "Knowledge Distillation via Constrained Variational Inference",
                "code_link": None,
                "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2022/03/ardavan_aaai22-600x248.png"
            }
        ]
    }
    
    # Read the full JSON from user input (we'll load it from a file or use the provided data)
    # For now, let's create a comprehensive mapping from all years
    base_dir = Path(__file__).parent
    index_html_path = base_dir / "index.html"
    images_dir = base_dir / "images" / "publications"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Load full JSON - we'll need to create this from the user's input
    # For now, let's work with the structure we have
    
    # Read HTML
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Build a mapping of all papers from JSON (we'll need the full JSON)
    # For now, let's process the papers we know about
    
    # First, download images for specified papers
    print("=" * 60)
    print("Downloading images for specified papers...")
    print("=" * 60)
    
    # Create a flat list of all papers from JSON
    all_papers = []
    for year, papers in json_data.items():
        for paper in papers:
            all_papers.append(paper)
    
    # Download images and update HTML
    for paper in all_papers:
        title = paper["title"]
        if title in PAPERS_TO_UPDATE_IMAGES and paper.get("image_icon_link"):
            img_url = paper["image_icon_link"]
            # Fix URL if it has double 'h' (like in Anatomy-Guided)
            if img_url.startswith('hhttps'):
                img_url = img_url[1:]
            
            # Create filename
            safe_title = sanitize_filename(title)
            # Determine extension from URL
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
                    # Update path to use downloaded filename
                    img_path = Path(downloaded_path)
                    relative_path = f"images/publications/{img_path.name}"
            
            # Update HTML
            html_content = update_image_in_html(html_content, title, relative_path)
    
    # Now update code links for ALL papers
    print("\n" + "=" * 60)
    print("Updating code links for all papers...")
    print("=" * 60)
    
    # We need to load the full JSON to get all code links
    # Let's check if there's a JSON file
    json_files = [
        base_dir / "publications_full.json",
        base_dir / "publications_data.json",
        base_dir / "publications_new.json"
    ]
    
    full_json_data = None
    for json_file in json_files:
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                full_json_data = json.load(f)
            print(f"✓ Loaded JSON from {json_file.name}")
            break
    
    if not full_json_data:
        print("⚠ No JSON file found. Using provided data structure.")
        full_json_data = json_data
    
    # Process all papers from JSON
    for year, papers in full_json_data.items():
        for paper in papers:
            title = paper.get("title", "")
            code_link = paper.get("code_link")
            
            if title:
                html_content = update_code_link_in_html(html_content, title, code_link)
    
    # Write updated HTML
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "=" * 60)
    print("✓ Successfully updated index.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
