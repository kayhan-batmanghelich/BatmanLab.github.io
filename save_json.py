import json
import sys

# Read JSON from stdin
json_text = sys.stdin.read()
data = json.loads(json_text)

# Save to file
with open('publications_complete.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("JSON saved to publications_complete.json")
