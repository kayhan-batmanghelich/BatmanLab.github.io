#!/usr/bin/env python3
"""
Script to generate HTML for publications section with correct image links, authors, and venues.
"""

import json
import html
from pathlib import Path

def format_authors(authors, highlight_name="Kayhan Batmanghelich"):
    """Format authors list, highlighting the specified name."""
    formatted = []
    for author in authors:
        if highlight_name.lower() in author.lower():
            formatted.append(f"<b>{html.escape(author)}</b>")
        else:
            formatted.append(html.escape(author))
    return ", ".join(formatted)

def generate_publications_html():
    """Generate HTML for publications section."""
    base_dir = Path(__file__).parent
    
    # Load data
    with open(base_dir / "publications_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(base_dir / "publication_image_mapping.json", 'r', encoding='utf-8') as f:
        image_mapping = json.load(f)
    
    html_parts = []
    
    # Process each year in reverse order
    for year in sorted(data.keys(), reverse=True):
        # Add year header
        html_parts.append(f'            <h4 class="mt-4 mb-3 fw-bold">{year}</h4>')
        
        for idx, pub in enumerate(data[year], 1):
            title = pub.get("title", "")
            authors = pub.get("authors", [])
            venue = pub.get("venue", "")
            paper_link = pub.get("paper_link", "")
            code_link = pub.get("code_link", "")
            preprint_link = pub.get("preprint_link", "")
            
            # Get image filename
            key = f"{year}_{idx}"
            img_filename = image_mapping.get(key, "")
            
            # Build image path
            if img_filename:
                img_path = f"images/publications/{img_filename}"
            else:
                # Use placeholder if no image
                img_path = "images/bu-logo.png"
            
            # Format authors
            authors_html = format_authors(authors)
            
            # Build meta links
            meta_links = []
            if paper_link and paper_link.strip():
                meta_links.append(f'<a href="{html.escape(paper_link)}"><i class="bi bi-file-earmark-text"></i> Paper</a>')
            if preprint_link and preprint_link.strip():
                meta_links.append(f'<a href="{html.escape(preprint_link)}"><i class="bi bi-cloud-download"></i> Preprint</a>')
            if code_link and code_link.strip():
                meta_links.append(f'<a href="{html.escape(code_link)}"><i class="bi bi-github"></i> Code</a>')
            
            meta_links_html = '<div class="meta-links mb-2">' + " ".join(meta_links) + '</div>' if meta_links else ''
            
            # Venue HTML - following template format
            venue_html = f'<div class="mb-1"><span class="fw-semibold">Venue:</span> {html.escape(venue)}</div>' if venue else ''
            
            # Generate HTML
            html_parts.append(f'''            <article class="item-row">
                <img src="{img_path}" alt="{html.escape(title)} thumbnail" onerror="this.src='images/bu-logo.png'">
                <div>
                    <h5 class="mb-1 fw-bold">{html.escape(title)}</h5>
                    <div class="muted mb-2">
                        {authors_html}
                    </div>
                    {venue_html}
                    {meta_links_html}
                </div>
            </article>''')
    
    return "\n".join(html_parts)

def main():
    html_content = generate_publications_html()
    
    # Save to file
    output_file = Path(__file__).parent / "publications_html_output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Publications HTML generated and saved to: {output_file}")
    print(f"\nTotal publications: {html_content.count('<article class=\"item-row\">')}")
    print("\nYou can now copy this HTML into your index.html file in the publications section.")

if __name__ == "__main__":
    main()
