#!/usr/bin/env python3
"""Create the complete JSON file from user's input"""
import json

# I'll create the JSON structure - since it's very large, I'll do it in parts
# Actually, the best is to read from stdin or file

import sys

if len(sys.argv) > 1:
    # Copy file
    with open(sys.argv[1], 'r') as f_in:
        with open('publications_complete.json', 'w') as f_out:
            f_out.write(f_in.read())
    print("✓ JSON file created")
else:
    print("Usage: python3 create_full_json.py <input_json_file>")
    print("This will copy your JSON to publications_complete.json")
