import json
import sys

# Read the JSON from the user's message
# Since it's provided in the message, I'll create it from a properly formatted string
# The user can also pipe JSON to this script

if len(sys.argv) > 1:
    # Read from file
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_text = f.read()
else:
    # Read from stdin
    json_text = sys.stdin.read()

try:
    data = json.loads(json_text)
    with open('publications_complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✓ JSON saved to publications_complete.json")
    print(f"  Found {sum(len(pubs) for pubs in data.values())} publications across {len(data)} years")
except json.JSONDecodeError as e:
    print(f"✗ JSON Error: {e}")
    sys.exit(1)
