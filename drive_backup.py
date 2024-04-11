import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Retrieve credentials for Google Drive API"""
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

    service = build('drive', 'v3', credentials=creds)
    return service


def upload_recursive(service, directory, uploaded_files, parent_folder_id=None):
    """Uploads subdirectories of the given directory to Google Drive"""
    for root, dirs, files in os.walk(directory):
        current_parent_folder_id = parent_folder_id

        for file in files:
            file_path = os.path.join(root, file)
            if file_path not in uploaded_files:
                upload_file(service, file_path, current_parent_folder_id)
                uploaded_files.add(file_path)
                tqdm.write(f"Uploading {file_path}")

        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            subdir_name = os.path.relpath(subdir_path, directory)
            folder_id = create_subdirectory(service, subdir_name, current_parent_folder_id)
            upload_recursive(service, subdir_path, uploaded_files, folder_id)




def create_subdirectory(service, subdir_name, parent_folder_id=None):
  """Creates a subdirectory folder in Google Drive (if it doesn't exist)"""
  query = f"name='{subdir_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
  if parent_folder_id:
    query += f" and '{parent_folder_id}' in parents"
  response = service.files().list(q=query).execute()
  existing_folders = response.get('files', [])
  if existing_folders:
    return existing_folders[0]['id']
  else:
    folder_metadata = {
      'name': subdir_name,
      'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
      folder_metadata['parents'] = [parent_folder_id]
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')

def upload_file(service, file_path, parent_folder_id=None):
    """Uploads a file to Google Drive"""
    file_metadata = {'name': os.path.basename(file_path)}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media).execute()


def upload_folder(service, folder_path, parent_folder_id=None):
    """Uploads a folder to Google Drive"""
    folder_name = os.path.basename(folder_path)
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    response = service.files().list(q=query).execute()
    existing_folders = response.get('files', [])
    if existing_folders:
        folder_id = existing_folders[0]['id']
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')

    return folder_id


def upload():
    """Backs up a folder from the local Desktop to Google Drive"""
    print("----------------------------------------------------------")
    print("---------------------- Drive Backup ----------------------")
    print("----------------------------------------------------------")
    desktop_path = os.path.expanduser('~/Desktop')
    service = authenticate()
    folder_name = 'Desktop Backup'
    backup_folder_id = create_backup_folder(service, folder_name)
    uploaded_files = set()
    upload_recursive(service, desktop_path, uploaded_files, backup_folder_id)
    print("Backup complete!")

def create_backup_folder(service, folder_name):
    """Creates or retrieves the backup folder in Google Drive"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    response = service.files().list(q=query).execute()
    items = response.get('files', [])

    if not items:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    else:
        return items[0]['id']

if __name__ == "__main__":
    upload()
