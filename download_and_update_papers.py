#!/usr/bin/env python3
"""
Script to download PDFs from batman-lab.com and update links to local files
"""

import re
import os
import urllib.request
import urllib.parse
from pathlib import Path
from urllib.error import URLError, HTTPError

html_path = Path("/Users/kayhan/Documents/Projects/newWebSite/index.html")
files_dir = Path("/Users/kayhan/Documents/Projects/newWebSite/files")

# Create files directory if it doesn't exist
files_dir.mkdir(exist_ok=True)

# Read the HTML file
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find all PDF links to batman-lab.com
pdf_pattern = r'href="(https://www\.batman-lab\.com/wp-content/uploads/[^"]+\.pdf)"'
pdf_urls = set(re.findall(pdf_pattern, html_content))

print(f"Found {len(pdf_urls)} unique PDF URLs to download")

# Download each PDF and create mapping
url_to_local = {}
failed_downloads = []

for pdf_url in sorted(pdf_urls):
    # Extract filename from URL
    filename = os.path.basename(urllib.parse.urlparse(pdf_url).path)
    
    # Create local file path
    local_path = files_dir / filename
    
    # Skip if already downloaded
    if local_path.exists():
        print(f"Already exists: {filename}")
        url_to_local[pdf_url] = f"files/{filename}"
        continue
    
    # Download the PDF
    try:
        print(f"Downloading: {filename}...")
        urllib.request.urlretrieve(pdf_url, local_path)
        print(f"  ✓ Downloaded: {filename}")
        url_to_local[pdf_url] = f"files/{filename}"
    except (URLError, HTTPError) as e:
        print(f"  ✗ Failed to download {filename}: {e}")
        failed_downloads.append((pdf_url, filename, str(e)))
        continue

print(f"\nSuccessfully downloaded {len(url_to_local)} files")
if failed_downloads:
    print(f"Failed to download {len(failed_downloads)} files:")
    for url, filename, error in failed_downloads:
        print(f"  - {filename}: {error}")

# Update HTML with local file paths
updated_html = html_content
for pdf_url, local_path in url_to_local.items():
    # Replace the URL with local path
    updated_html = updated_html.replace(f'href="{pdf_url}"', f'href="{local_path}"')

# Write updated HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(updated_html)

print(f"\nUpdated {html_path} with local file paths")
