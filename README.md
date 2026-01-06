# salesforcecmsbulkupload
uploading content at scale to salesforce cms

# Salesforce CMS Bulk Image Bundler

A simple web tool to prepare images for bulk import into Salesforce Enhanced CMS.

## How to use
1. Go to the [Live App URL](https://salesforce-cms-bulk-upload-90dd3eca8982.herokuapp.com/).
2. Select your images (JPG, PNG).
3. **Check the Traffic Light:**
   - ✅ **Green:** Safe to upload.
   - ⚠️ **Orange:** Might timeout (try splitting the batch).
   - ⛔ **Red:** Too big (please split the batch).
4. Click **Convert & Download**.
5. Upload the resulting ZIP file to your Salesforce CMS Workspace.

## Technical Details
- Built with Python (Flask).
- Hosting: Heroku.
- Formats images into the **Enhanced CMS** JSON structure (one folder per item).
