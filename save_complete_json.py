#!/usr/bin/env python3
"""
Helper script to save the complete JSON data provided by the user.
This will be used by the update script.
"""

import json
import sys

# The user provided complete JSON - we'll read it from stdin or a file
if len(sys.argv) > 1:
    # Read from file
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_text = f.read()
else:
    # For now, we'll create a minimal version and the user can provide the full JSON
    # Or we can read from a file they create
    print("Usage: python3 save_complete_json.py <json_file>")
    print("Or pipe JSON to stdin")
    sys.exit(1)

try:
    data = json.loads(json_text)
    output_file = 'publications_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON saved to {output_file}")
    print(f"  Found {sum(len(pubs) for pubs in data.values())} publications across {len(data)} years")
except json.JSONDecodeError as e:
    print(f"✗ JSON Error: {e}")
    sys.exit(1)
