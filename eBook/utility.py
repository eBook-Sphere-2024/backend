import fitz  # PyMuPDF
from PIL import Image
import io
import os
from tempfile import NamedTemporaryFile
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# Function to upload eBook PDF file for review
def uploadEbookForReview(pdf_file, folderId, fileName):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': fileName,
        'parents': [folderId]
    }

    media = MediaIoBaseUpload(io.BytesIO(pdf_file.read()), mimetype='application/pdf')

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return uploaded_file.get('id')

# Function to move file in Google Drive
def move_file_in_google_drive(fileId, folderIdToUpload):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)

    file = service.files().get(fileId=fileId, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    file = service.files().update(
        fileId=fileId,
        addParents=folderIdToUpload,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()

    return file.get('id')

def moveCoverInGoogleDrive(fileId, coverFolderIdToUpload):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)

    file = service.files().get(fileId=fileId, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    file = service.files().update(
        fileId=fileId,
        addParents=coverFolderIdToUpload,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()

    return file.get('id')

# Function to download file from Google Drive
def download_file_from_google_drive(file_id):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Get the file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        
        # Download the file content
        request = service.files().get_media(fileId=file_id)
        file_bytes = io.BytesIO()
        downloader = MediaIoBaseDownload(file_bytes, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        return file_bytes
    except Exception as e:
        print(f"Error downloading file from Google Drive: {str(e)}")
        return None

# Function to extract the first page of a PDF as an image
def extract_first_page_as_image(pdf_file_bytes, output_image_path):
    try:
        # Create a temporary PDF file
        with NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
            temp_pdf_path = temp_pdf_file.name
            temp_pdf_file.write(pdf_file_bytes.getvalue())
        
        print(f"Temporary PDF path: {temp_pdf_path}")
        
        # Open the PDF file
        doc = fitz.open(temp_pdf_path)
        
        # Extract the first page
        first_page = doc.load_page(0)
        
        # Convert the page to a pixmap
        pix = first_page.get_pixmap()
        
        print(f"Pixmap format: {pix.colorspace} - {pix.alpha}")
        print(f"Pixmap size: {pix.width} x {pix.height} pixels")
        
        # Convert the Pixmap to PIL Image
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        
        # Save the image as PNG
        img.save(output_image_path, format="PNG")
        
        print(f"First page extracted and saved as {output_image_path}")
        
        # Delete temporary PDF file
        os.remove(temp_pdf_path)
        
    except Exception as e:
        print(f"Error extracting and saving first page as image: {str(e)}")
        return None


# Function to upload an image to Google Drive
def upload_image_to_google_drive(image_path, folder_id, file_name):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    with open(image_path, 'rb') as image_file:
        media = MediaIoBaseUpload(io.BytesIO(image_file.read()), mimetype='image/png')

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

    return uploaded_file.get('id')

def process_and_upload_cover_image(file_id, folder_id, cover_folder_id, cover_file_name):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Download the PDF file content
        pdf_file_bytes = download_file_from_google_drive(file_id)
        
        if pdf_file_bytes is None:
            print("Failed to download PDF file.")
            return None
        
        # Create a temporary image file path
        temp_image_path = NamedTemporaryFile(suffix='.png', delete=False).name
        
        # Extract the cover image from the PDF
        extract_first_page_as_image(pdf_file_bytes, temp_image_path)
        
        if not os.path.exists(temp_image_path):
            print("Failed to extract cover image.")
            return None
        
        # Upload the extracted cover image to Google Drive
        cover_image_id = upload_image_to_google_drive(temp_image_path, cover_folder_id, cover_file_name)
        
        # Delete temporary image file
        os.remove(temp_image_path)
        
        return cover_image_id
    
    except Exception as e:
        print(f"Error processing and uploading cover image: {str(e)}")
        return None

def delete_file_in_google_drive(file_id):
    service_account_file = 'eBook/credential.json'
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    service.files().delete(fileId=file_id).execute()
    print(f"File {file_id} deleted successfully.")