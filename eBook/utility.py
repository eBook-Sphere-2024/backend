from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

#to upload to review folder
def uploadEbookForReview(file,folderId,fileName):
    # Define the path to your service account JSON key file
    service_account_file = 'eBook/credential.json'
    # Authenticate the application with Google Drive API using service account credentials
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    # Define file metadata
    file_metadata = {
        'name': fileName,
        'parents': [folderId]
    }

    # Create a MediaIoBaseUpload object with the file content
    media = MediaIoBaseUpload(io.BytesIO(file.read()), mimetype='application/pdf')

    # Upload the file to Google Drive
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Return the file ID of the uploaded file
    return uploaded_file.get('id')

#to upload to ebook folder
def move_file_in_google_drive(fileId, folderIdToUpload):
    # Define the path to your service account JSON key file
    service_account_file = 'eBook/credential.json'
    
    # Authenticate the application with Google Drive API using service account credentials
    creds = Credentials.from_service_account_file(service_account_file)
    service = build('drive', 'v3', credentials=creds)
    
    # Retrieve the existing parents to remove
    file = service.files().get(fileId=fileId, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    
    # Move the file to the new folder
    file = service.files().update(
        fileId=fileId,
        addParents=folderIdToUpload,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()
    
    return file.get('id')