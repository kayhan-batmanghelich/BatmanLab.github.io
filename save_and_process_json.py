#!/usr/bin/env python3
"""
Save JSON from stdin and process it immediately.
Usage: paste your JSON and pipe to this script, or provide as file argument.
"""

import json
import sys
import subprocess

# Read JSON
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_text = f.read()
else:
    json_text = sys.stdin.read()

try:
    data = json.loads(json_text)
    
    # Save to file
    with open('publications_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ JSON saved to publications_complete.json")
    print(f"  Found {sum(len(pubs) for pubs in data.values())} publications across {len(data)} years")
    
    # Now process it
    print("\nProcessing publications...")
    result = subprocess.run(['python3', 'process_publications.py', 'publications_complete.json'], 
                          capture_output=False)
    
except json.JSONDecodeError as e:
    print(f"✗ JSON Error: {e}")
    sys.exit(1)
