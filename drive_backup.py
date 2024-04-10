"""Drive Backup Module"""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def backup_folder():
    """Backs up a folder from the local Desktop to Google Drive"""
    print("----------------Drive Backup---------------")
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)

    response = service.files().list(
        q="name='Desktop Backup' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()

    if not response['files']:
        file_metadata = {
            "name": "Desktop Backup",
            "mimeType": "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = file.get('id')
    else:
        folder_id = response['files'][0]['id']

    def backup_directory(directory_path, parent_folder_id):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                item_metadata = {
                    "name": item,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [parent_folder_id]
                }
                item_file = service.files().create(body=item_metadata, fields="id").execute()
                item_folder_id = item_file.get('id')
                backup_directory(item_path, item_folder_id)
            else:
                file_metadata = {
                    "name": item,
                    "parents": [parent_folder_id]
                }
                media = MediaFileUpload(item_path)
                upload_file = service.files().create(body=file_metadata,
                                                      media_body=media,
                                                      fields="id").execute()
                print(f"Backed up file: {os.path.basename(item_path)} to Google Drive")

    parent_dir = os.path.expanduser("~/Desktop")
    backup_directory(parent_dir, folder_id)

if __name__ == "__main__":
    backup_folder()
