#!/usr/bin/env python3
"""
Script to update publication links in index.html based on publication_link.json
"""

import json
import re
from pathlib import Path

# Load the JSON file with correct links
json_path = Path("/Users/kayhan/Downloads/publication_link.json")
html_path = Path("/Users/kayhan/Documents/Projects/newWebSite/index.html")

with open(json_path, 'r', encoding='utf-8') as f:
    publications_data = json.load(f)

# Read the HTML file
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

def normalize_title(title):
    """Normalize title for matching"""
    # Remove HTML entities
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # Remove extra whitespace
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
        if normalize_title(pub['title']) == normalized_title:
            return pub
    
    # Try fuzzy matching - check if significant words match
    title_words = set(normalized_title.split())
    if len(title_words) < 3:
        return None
    
    best_match = None
    best_score = 0
    
    for pub in publications_data[year_str]:
        pub_title_norm = normalize_title(pub['title'])
        pub_words = set(pub_title_norm.split())
        
        if len(pub_words) == 0:
            continue
        
        # Calculate overlap
        overlap = len(title_words & pub_words)
        total_words = min(len(title_words), len(pub_words))
        
        if total_words > 0:
            score = overlap / total_words
            if score > best_score and score > 0.6:  # At least 60% word overlap
                best_score = score
                best_match = pub
    
    return best_match

def build_meta_links_html(paper_link, preprint_link, code_link, project_link):
    """Build the meta-links HTML string"""
    links = []
    
    if paper_link and paper_link.strip():
        links.append(f'<a href="{paper_link}"><i class="bi bi-file-earmark-text"></i> Paper</a>')
    
    if preprint_link and preprint_link.strip():
        links.append(f'<a href="{preprint_link}"><i class="bi bi-cloud-download"></i> Preprint</a>')
    
    if code_link and code_link.strip():
        links.append(f'<a href="{code_link}"><i class="bi bi-github"></i> Code</a>')
    
    if project_link and project_link.strip():
        links.append(f'<a href="{project_link}"><i class="bi bi-box-arrow-up-right"></i> Project</a>')
    
    if links:
        return f'<div class="meta-links mb-2">{" ".join(links)}</div>'
    return ''

# First, remove all duplicate meta-links divs
# Find all meta-links and keep only the first one in each article
def remove_duplicate_meta_links(content):
    """Remove duplicate meta-links divs from articles"""
    # Pattern to match article with potential duplicate meta-links
    article_pattern = r'(<article class="item-row">.*?</article>)'
    
    def clean_article(match):
        article = match.group(1)
        # Find all meta-links divs
        meta_pattern = r'(<div class="meta-links mb-2">.*?</div>)'
        meta_matches = list(re.finditer(meta_pattern, article, flags=re.DOTALL))
        
        if len(meta_matches) <= 1:
            return article  # No duplicates
        
        # Keep only the first one, remove the rest
        result = article
        # Replace from end to start to avoid position shifting
        for i in range(len(meta_matches) - 1, 0, -1):
            meta_match = meta_matches[i]
            # Remove this duplicate (including any leading whitespace/newlines)
            start = meta_match.start()
            end = meta_match.end()
            # Also remove preceding whitespace/newlines
            while start > 0 and result[start-1] in ' \n\t':
                start -= 1
            result = result[:start] + result[end:]
        
        return result
    
    return re.sub(article_pattern, clean_article, content, flags=re.DOTALL)

# Remove duplicates first
html_content = remove_duplicate_meta_links(html_content)

# Now process each article to update links
# Find all year sections
year_sections = list(re.finditer(r'<h4 class="mt-4 mb-3 fw-bold">(\d{4})</h4>', html_content))

if not year_sections:
    print("No year sections found!")
    exit(1)

# Process from end to start to avoid position shifting
result_content = html_content

for i in range(len(year_sections) - 1, -1, -1):
    year_match = year_sections[i]
    year = year_match.group(1)
    year_start = year_match.start()
    
    # Find the end of this year's section
    if i < len(year_sections) - 1:
        section_end = year_sections[i + 1].start()
    else:
        # Last year - find end of publications section
        section_end_match = re.search(r'</section>', result_content[year_start:])
        if section_end_match:
            section_end = year_start + section_end_match.start()
        else:
            section_end = len(result_content)
    
    year_section = result_content[year_start:section_end]
    
    # Process articles in this year
    article_pattern = r'(<article class="item-row">.*?<h5 class="mb-1 fw-bold">(.*?)</h5>.*?<div class="mb-1"><span class="fw-semibold">Venue:</span>.*?</div>)(.*?)(</article>)'
    
    def replace_article(match):
        before_meta = match.group(1)
        article_middle = match.group(3)
        article_end = match.group(4)
        
        # Extract title
        title_match = re.search(r'<h5 class="mb-1 fw-bold">(.*?)</h5>', before_meta)
        if not title_match:
            return match.group(0)
        
        title = title_match.group(1)
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        
        # Find matching publication
        pub_data = find_publication_in_json(title_clean, year)
        
        if pub_data:
            # Build new meta links
            new_meta = build_meta_links_html(
                pub_data.get('paper_link', ''),
                pub_data.get('preprint_link', ''),
                pub_data.get('code_link', ''),
                pub_data.get('project_link', '')
            )
            
            if new_meta:
                # Remove any existing meta-links from article_middle
                article_middle_clean = re.sub(r'<div class="meta-links mb-2">.*?</div>', '', article_middle, flags=re.DOTALL)
                # Add new meta links
                return before_meta + '\n                    ' + new_meta + article_middle_clean + article_end
        
        # No match - return original (but clean up any duplicates)
        article_middle_clean = article_middle
        meta_count = len(re.findall(r'<div class="meta-links mb-2">', article_middle))
        if meta_count > 1:
            # Keep only the first one
            parts = re.split(r'(<div class="meta-links mb-2">.*?</div>)', article_middle, flags=re.DOTALL, maxsplit=1)
            if len(parts) >= 2:
                article_middle_clean = parts[0] + parts[1] + ''.join(parts[2:])
        
        return before_meta + article_middle_clean + article_end
    
    # Replace articles in this section
    updated_section = re.sub(article_pattern, replace_article, year_section, flags=re.DOTALL)
    
    # Replace the section in the main content
    result_content = result_content[:year_start] + updated_section + result_content[section_end:]

# Write back to file
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(result_content)

print(f"Updated publication links in {html_path}")
print("Please review the changes before committing.")
