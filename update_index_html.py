#!/usr/bin/env python3
"""
Script to update index.html with the correct publications HTML.
"""

from pathlib import Path
import re

def main():
    base_dir = Path(__file__).parent
    
    # Read the generated HTML
    with open(base_dir / "publications_html_output.txt", 'r', encoding='utf-8') as f:
        new_publications_html = f.read()
    
    # Read the current index.html
    with open(base_dir / "index.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the publications section
    # Pattern: from <div class="d-grid gap-3"> to </div> before </section>
    pattern = r'(<div class="d-grid gap-3">\s*)(.*?)(\s*</div>\s*</section>\s*<!-- LAB MEMBERS)'
    
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        # Replace the content between the div tags
        replacement = match.group(1) + "\n" + new_publications_html + "\n" + match.group(3)
        html_content = html_content[:match.start()] + replacement + html_content[match.end():]
        
        # Write back
        with open(base_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✓ Successfully updated index.html with new publications")
        print(f"  Replaced publications section with {new_publications_html.count('<article')} publications")
    else:
        print("✗ Could not find publications section boundaries")
        print("  Looking for pattern: <div class=\"d-grid gap-3\"> ... </div> </section> <!-- LAB MEMBERS")

if __name__ == "__main__":
    main()
