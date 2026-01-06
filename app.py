import os
import json
import zipfile
import io
import re
import mimetypes
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- CONFIGURATION ---
# Enhanced CMS uses specific type names
CMS_TYPE = 'sfdc_cms__image'
# ---------------------

def sanitize_slug(filename):
    """Creates a clean, URL-friendly slug from a filename."""
    name = os.path.splitext(filename)[0]
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'images' not in request.files:
        return "No files uploaded", 400

    uploaded_files = request.files.getlist('images')
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No selected files", 400

    # We use BytesIO to create the ZIP in RAM
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_storage in uploaded_files:
            filename = file_storage.filename
            
            # 1. Validation & Setup
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            # Determine Mime Type (Required for Enhanced CMS)
            mime_type = mimetypes.guess_type(filename)[0]
            if not mime_type:
                mime_type = 'image/jpeg' # Fallback

            # 2. Prepare Names
            slug = sanitize_slug(filename)
            title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()
            
            # 3. Create Folder Structure for this specific item
            # Structure: [slug]/_media/[filename]
            # Structure: [slug]/content.json
            item_folder = slug
            zip_media_path = f"{item_folder}/_media/{filename}"
            zip_json_path = f"{item_folder}/content.json"

            # 4. Build JSON Object (Enhanced CMS Format)
            # Note: Enhanced CMS does NOT use a specific "ref" path in the JSON for the file.
            # It expects the file to be in the relative _media folder, and we simply declare type='file'.
            entry = {
                "type": CMS_TYPE,
                "title": title,
                "contentBody": {
                    "sfdc_cms:media": {
                        "source": {
                            "type": "file",
                            "mimeType": mime_type
                        }
                    }
                }
            }

            # 5. Write to Zip
            # Add Image
            zipf.writestr(zip_media_path, file_storage.read())
            # Add JSON
            zipf.writestr(zip_json_path, json.dumps(entry, indent=4))

    # Reset pointer
    memory_file.seek(0)

    return send_file(
        memory_file,
        download_name='salesforce_enhanced_cms_import.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
