import os
import json
import zipfile
import io
import re
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- CONFIGURATION ---
CMS_TYPE = 'cms_image'
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

    # We use BytesIO to create the ZIP in RAM, not on the hard drive
    memory_file = io.BytesIO()
    
    content_entries = []

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_storage in uploaded_files:
            filename = file_storage.filename
            
            # Basic validation
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            # 1. Prepare Metadata
            slug = sanitize_slug(filename)
            title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()
            zip_media_path = f"_media/{filename}"

            # 2. Build JSON Object
            entry = {
                "type": CMS_TYPE,
                "urlName": slug,
                "status": "Draft",
                "body": {
                    "title": title,
                    "altText": title,
                    "source": {
                        "ref": zip_media_path
                    }
                }
            }
            content_entries.append(entry)

            # 3. Add image to ZIP (read directly from upload stream)
            zipf.writestr(zip_media_path, file_storage.read())

        # 4. Add content.json to ZIP
        json_data = {"content": content_entries}
        zipf.writestr('content.json', json.dumps(json_data, indent=4))

    # Reset pointer to beginning of the memory file so it can be read
    memory_file.seek(0)

    return send_file(
        memory_file,
        download_name='salesforce_cms_import.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

if __name__ == '__main__':
    # Threaded=True helps with multiple concurrent uploads locally
    app.run(debug=True, threaded=True)
