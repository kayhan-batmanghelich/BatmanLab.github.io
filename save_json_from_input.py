#!/usr/bin/env python3
"""Save JSON from user's input and process it"""
import json
import sys

# Read from stdin or file argument
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_text = f.read()
else:
    json_text = sys.stdin.read()

try:
    # Parse and save
    data = json.loads(json_text)
    with open('publications_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved JSON: {sum(len(pubs) for pubs in data.values())} publications")
    return True
except Exception as e:
    print(f"✗ Error: {e}")
    return False
