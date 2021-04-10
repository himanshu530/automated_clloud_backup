import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload
from datetime import datetime
import os


class MyDrive():
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self,page_size=10):
            # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
    
    def upload_files(self,filename,path):

        flag = 0

        folder_id = "1G0oukOhiLXfazn2nrQCyVFZgweOhcSUV"
        media = MediaFileUpload(f"{path}{filename}")

        response = self.service.files().list(
            q=f"name='{filename}' and parents='{folder_id}'",
            spaces='drive',
            fields='nextPageToken,files(id,name)',
            pageToken = None
           ).execute()

        if len(response['files']) == 0:
            file_metadata = {
                'name':filename,
                'parents':[folder_id]
            }
            file = self.service.files().create(body=file_metadata,media_body=media,fields='id').execute()
            print(f"A new file was created in backup, {file.get('id')}")
            flag = 1
        else:
            for file in response.get('files',[]):
                update_file = self.service.files().update(
                    fileId = file.get('id'),
                    media_body = media
                ).execute()
                print(update_file)
                print(f"File Updated")
                flag = 1
        myfile = open("Backup_log.txt","a")
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        if(flag):
            myfile.write(date_time+" backup_successful "+path+"\n")
        else:
            myfile.write(date_time+" backup_failed due to network/path error \n")
        
        myfile.close()







def main():

    path="C:/Users/HIMANSHU/Desktop/Backup/"
    files = os.listdir(path)
    my_drive = MyDrive()
    # my_drive.list_files()

    for itr in files:
        my_drive.upload_files(itr,path)
    

    

if __name__ == '__main__':
    main()