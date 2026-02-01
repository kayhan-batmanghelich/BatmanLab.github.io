# Processing Publications

## Steps to update publications:

1. **Save your JSON** to a file named `publications_complete.json`

2. **Run the processing script:**
   ```bash
   python3 process_publications.py publications_complete.json
   ```

The script will:
- ✓ Delete all old images in `images/publications/`
- ✓ Download all images with correct sequential numbering matching HTML
- ✓ Generate HTML with venues included (between authors and links)
- ✓ Update `index.html` automatically

## Venue Format

Venues are displayed as:
```html
<div class="mb-2"><span class="fw-semibold">Venue:</span> <em>Venue Name</em></div>
```

This appears between the authors and the meta links (Paper/Preprint/Code/BibTeX).
