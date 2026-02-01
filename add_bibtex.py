#!/usr/bin/env python3
"""
Script to add BibTeX to publications in index.html from publications_complete.json
"""

import json
import re
from pathlib import Path
from html import escape

# File paths
json_path = Path("/Users/kayhan/Documents/Projects/newWebSite/publications_complete.json")
html_path = Path("/Users/kayhan/Documents/Projects/newWebSite/index.html")

# Load JSON data
with open(json_path, 'r', encoding='utf-8') as f:
    publications_data = json.load(f)

# Read HTML
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

def normalize_title(title):
    """Normalize title for matching"""
    # Remove HTML entities and tags
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    title = re.sub(r'\s+', ' ', title.strip())
    return title.lower()

def find_publication_in_json(title, year):
    """Find matching publication in JSON data"""
    year_str = str(year)
    if year_str not in publications_data:
        return None
    
    normalized_title = normalize_title(title)
    
    # First try exact match
    for pub in publications_data[year_str]:
        if normalize_title(pub.get('title', '')) == normalized_title:
            return pub
    
    # Try fuzzy matching
    title_words = set(normalized_title.split())
    if len(title_words) < 3:
        return None
    
    best_match = None
    best_score = 0
    
    for pub in publications_data[year_str]:
        pub_title_norm = normalize_title(pub.get('title', ''))
        pub_words = set(pub_title_norm.split())
        
        if len(pub_words) == 0:
            continue
        
        overlap = len(title_words & pub_words)
        total_words = min(len(title_words), len(pub_words))
        
        if total_words > 0:
            score = overlap / total_words
            if score > best_score and score > 0.6:
                best_score = score
                best_match = pub
    
    return best_match

def format_bibtex_html(bibtex_text):
    """Format BibTeX text as HTML with proper escaping"""
    # Replace \n with actual newlines
    bibtex_text = bibtex_text.replace('\\n', '\n')
    # Escape HTML special characters
    bibtex_escaped = escape(bibtex_text)
    
    # Generate unique ID for this BibTeX section
    import random
    bibtex_id = f"bibtex_{random.randint(10000, 99999)}"
    
    return f'''<div class="bibtex-section mt-2">
                    <button class="btn btn-sm btn-outline-secondary mb-2" type="button" onclick="toggleBibtex('{bibtex_id}')">
                        Show BibTeX
                    </button>
                    <pre id="{bibtex_id}" style="display: none; background: var(--bg-soft); padding: 12px; border-radius: 8px; border: 1px solid var(--card-border); font-size: 0.85rem; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word;"><code>{bibtex_escaped}</code></pre>
                </div>'''

# Find all year sections
year_sections = list(re.finditer(r'<h4 class="mt-4 mb-3 fw-bold">(\d{4})</h4>', html_content))

if not year_sections:
    print("No year sections found!")
    exit(1)

result_content = html_content

# Process from end to start to avoid position shifting
for i in range(len(year_sections) - 1, -1, -1):
    year_match = year_sections[i]
    year = year_match.group(1)
    year_start = year_match.start()
    
    # Find the end of this year's section
    if i < len(year_sections) - 1:
        section_end = year_sections[i + 1].start()
    else:
        section_end_match = re.search(r'</section>', result_content[year_start:])
        if section_end_match:
            section_end = year_start + section_end_match.start()
        else:
            section_end = len(result_content)
    
    year_section = result_content[year_start:section_end]
    
    # Process articles in this year
    # Pattern to match article with meta-links
    article_pattern = r'(<article class="item-row">.*?<h5 class="mb-1 fw-bold">(.*?)</h5>.*?<div class="meta-links mb-2">.*?</div>)(.*?)(</article>)'
    
    def add_bibtex_to_article(match):
        before_end = match.group(1)
        article_middle = match.group(3)
        article_end = match.group(4)
        
        # Extract title
        title_match = re.search(r'<h5 class="mb-1 fw-bold">(.*?)</h5>', before_end)
        if not title_match:
            return match.group(0)
        
        title = title_match.group(1)
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        
        # Find matching publication
        pub_data = find_publication_in_json(title_clean, year)
        
        if pub_data and pub_data.get('bibtex'):
            bibtex_html = format_bibtex_html(pub_data['bibtex'])
            # Check if BibTeX already exists
            if 'bibtex-section' not in article_middle:
                # Add BibTeX after meta-links, before article end
                return before_end + '\n                    ' + bibtex_html + article_middle + article_end
        
        return match.group(0)
    
    # Replace articles in this section
    updated_section = re.sub(article_pattern, add_bibtex_to_article, year_section, flags=re.DOTALL)
    
    # Replace the section in the main content
    result_content = result_content[:year_start] + updated_section + result_content[section_end:]

# Add JavaScript function for toggling BibTeX if not present
if 'function toggleBibtex' not in result_content:
    # Find the closing script tag or add before </body>
    if '</body>' in result_content:
        toggle_script = '''
<script>
function toggleBibtex(id) {
    const element = document.getElementById(id);
    const button = element.previousElementSibling;
    if (element.style.display === 'none') {
        element.style.display = 'block';
        button.textContent = 'Hide BibTeX';
    } else {
        element.style.display = 'none';
        button.textContent = 'Show BibTeX';
    }
}
</script>
'''
        result_content = result_content.replace('</body>', toggle_script + '</body>')

# Write updated HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(result_content)

print(f"Added BibTeX to publications in {html_path}")
print("Please review the changes.")
