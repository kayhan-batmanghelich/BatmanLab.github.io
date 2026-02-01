import urllib.request

# Test the exact URL from user's example
url = "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.39.24%E2%80%AFPM-600x178.png"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        print(f"✓ Success! Status: {response.status}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content-Length: {response.headers.get('Content-Length')} bytes")
        # Save it
        with open('test_medsyn.png', 'wb') as f:
            f.write(response.read())
        print(f"  Saved to: test_medsyn.png")
except Exception as e:
    print(f"✗ Error: {e}")
