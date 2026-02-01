#!/usr/bin/env python3
"""
Regenerate publications section with correct images and venues from JSON.
"""

import json
import urllib.request
import base64
from pathlib import Path

def download_image(url, filename):
    """Download image from URL exactly as provided"""
    if not url or url == "":
        return False
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                with open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                return True
    except:
        return False
    return False

def format_authors(authors_list):
    formatted = []
    for author in authors_list:
        if "Kayhan" in author or "Batmanghelich" in author:
            formatted.append(f"<b>{author}</b>")
        else:
            formatted.append(author)
    return ", ".join(formatted)

# Read JSON from file (user will provide full JSON)
import sys
if len(sys.argv) > 1:
    json_file = sys.argv[1]
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    # Try to read from stdin or default file
    try:
        with open('publications_full.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("Error: Please provide JSON file as argument or save as publications_full.json")
        sys.exit(1)

# Create images directory
images_dir = Path("images/publications")
images_dir.mkdir(parents=True, exist_ok=True)

# Generate HTML and download images
html_parts = []
seq_num = 1
downloaded = 0
failed = 0

for year in sorted(data.keys(), reverse=True):
    html_parts.append(f'            <h4 class="mt-4 mb-3 fw-bold">{year}</h4>')
    
    for pub in data[year]:
        # Download image
        img_url = pub.get("image_icon_link", "")
        if img_url:
            if img_url.endswith('.jpg') or img_url.endswith('.jpeg'):
                img_filename = f"pub_{year}_{seq_num}.jpg"
            else:
                img_filename = f"pub_{year}_{seq_num}.png"
            
            img_path = images_dir / img_filename
            if not img_path.exists():
                if download_image(img_url, str(img_path)):
                    downloaded += 1
                    print(f"✓ Downloaded: {img_filename}")
                else:
                    failed += 1
                    print(f"✗ Failed: {img_url[:60]}...")
        else:
            img_filename = f"pub_{year}_{seq_num}.png"
        
        # Format authors
        authors_html = format_authors(pub["authors"])
        
        # Build meta links
        meta_links = []
        if pub.get("paper_link") and pub["paper_link"]:
            meta_links.append(f'<a href="{pub["paper_link"]}"><i class="bi bi-file-earmark-text"></i> Paper</a>')
        if pub.get("preprint_link") and pub["preprint_link"]:
            meta_links.append(f'<a href="{pub["preprint_link"]}"><i class="bi bi-cloud-download"></i> Preprint</a>')
        if pub.get("code_link") and pub["code_link"]:
            meta_links.append(f'<a href="{pub["code_link"]}"><i class="bi bi-github"></i> Code</a>')
        if pub.get("bibtex") and pub["bibtex"]:
            bibtex_text = pub["bibtex"]
            bibtex_b64 = base64.b64encode(bibtex_text.encode('utf-8')).decode('utf-8')
            safe_title = "".join(c for c in pub["title"][:50] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
            meta_links.append(f'<a href="data:text/plain;base64,{bibtex_b64}" download="{safe_title}.bib"><i class="bi bi-file-text"></i> BibTeX</a>')
        
        meta_links_html = '<div class="meta-links mb-2">' + " ".join(meta_links) + '</div>' if meta_links else ''
        
        # Add venue
        venue_html = ''
        venue = pub.get("venue", "")
        if venue:
            venue_html = f'<div class="mb-2"><span class="fw-semibold">Venue:</span> <em>{venue}</em></div>'
        
        # Generate HTML
        html_parts.append(f'''            <article class="item-row">
                <img src="images/publications/{img_filename}" alt="{pub["title"]} thumbnail" onerror="this.src='images/bu-logo.png'">
                <div>
                    <h5 class="mb-1 fw-bold">{pub["title"]}</h5>
                    <div class="muted mb-2">
                        {authors_html}
                    </div>
                    {venue_html}
                    {meta_links_html}
                </div>
            </article>''')
        
        seq_num += 1

# Write HTML to file
with open("publications_html_new.txt", "w", encoding='utf-8') as f:
    f.write("\n".join(html_parts))

print(f"\n{'='*60}")
print(f"Summary: {downloaded} downloaded, {failed} failed, {seq_num-1} total publications")
print(f"HTML saved to publications_html_new.txt")
print(f"{'='*60}")
