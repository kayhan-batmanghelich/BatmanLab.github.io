import json
import urllib.request
from pathlib import Path

# Read the JSON file (we'll need to recreate it or read from the user's input)
# For now, let's create a script that downloads all images

def download_image(url, filename):
    """Download image from URL exactly as provided"""
    if not url or url == "":
        return False
    try:
        # Use URL exactly as provided - don't decode/encode it
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                with open(filename, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"✓ Downloaded: {filename}")
                return True
            else:
                print(f"✗ HTTP {response.status} for {filename}")
                return False
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

# Create images directory
images_dir = Path("images/publications")
images_dir.mkdir(parents=True, exist_ok=True)

# JSON data with all publications
json_data = """{
  "2024": [
    {
      "title": "MedSyn: Text-guided Anatomy-aware Synthesis of High-Fidelity 3D CT Images",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.39.24%E2%80%AFPM-600x178.png"
    },
    {
      "title": "Mammo-CLIP: A Vision Language Foundation Model to Enhance Data Efficiency and Robustness in Mammography",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.43.25%E2%80%AFPM-600x435.png"
    },
    {
      "title": "Anatomy-specific Progression Classification in Chest Radiographs via Weakly Supervised Learning",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/10/Screenshot-2024-10-17-at-10.59.40%E2%80%AFPM-600x230.png"
    }
  ],
  "2023": [
    {
      "title": "Semi-Implicit Denoising Diffusion Models (SIDDMs)",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-3.47.53%E2%80%AFPM-300x92.png"
    },
    {
      "title": "DrasCLR: Self-Supervised Representation Learning via Disentangled Representations and Spectral Clustering",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-2.49.14%E2%80%AFPM-600x467.png"
    },
    {
      "title": "Beyond Distribution Shift: Spurious Features Through the Lens of Training Dynamics",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/kmnist_expts-300x161.jpg"
    },
    {
      "title": "ComBat Harmonization: Empirical Bayes versus fully Bayes approaches",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2024/01/Screenshot-2024-01-07-at-3.12.49%E2%80%AFPM-600x435.png"
    },
    {
      "title": "Distilling Blackbox to Interpretable Models for Efficient Transfer Learning",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/Screenshot-2023-10-10-at-11.31.06%E2%80%AFPM-300x159.png"
    },
    {
      "title": "Physics-Informed Neural Networks for Tissue Elasticity Reconstruction in Magnetic Resonance Elastography",
      "image_icon_link": "https://www.batman-lab.com/wp-content/uploads/2023/10/Screenshot-2023-10-10-at-11.45.54%E2%80%AFPM-300x96.png"
    }
  ]
}"""

data = json.loads(json_data)

# Download all images
pub_counter = 0
for year in sorted(data.keys(), reverse=True):
    for pub in data[year]:
        pub_counter += 1
        img_url = pub.get("image_icon_link", "")
        if img_url:
            img_filename = f"pub_{year}_{pub_counter}.png"
            # Handle .jpg extension
            if img_url.endswith('.jpg'):
                img_filename = img_filename.replace('.png', '.jpg')
            img_path = images_dir / img_filename
            
            if not img_path.exists():
                download_image(img_url, str(img_path))
            else:
                print(f"⊘ Already exists: {img_filename}")

print(f"\nDownload process complete!")
