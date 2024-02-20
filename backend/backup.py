# A python script to backup my postgresql database to a file
# the postgress database is in a docker container
# the backup file is saved in a remote server

import os
import glob
import subprocess
import datetime
import time
import sys
import logging
import logging.handlers
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter('%(module)s.%(funcName)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Set up database
db_name = 'digifolk'
db_user = 'digifolk_admin'
db_password = 'digifolk2023'

# Set up backup
backup_dir = '/home/marianavarro/backup'

# Set the scopes required for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

    
# Set up backup
def backup(container_name):
    # Get current date and time
    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Define the backup file path
    backup_file = os.path.join(backup_dir, f"{container_name}_backup_{current_datetime}.sql")

    # Command to execute pg_dump inside the PostgreSQL container
    command = [
        "docker", "exec", container_name,
        "bash", "-c",
        f"export PGPASSWORD='{db_password}' && pg_dump --username={db_user} {db_name}"
    ]

    # Redirect the output of the pg_dump command to a file
    with open(backup_file, "w") as file:
        subprocess.run(command, stdout=file)

    print(f"Backup created successfully at: {backup_file}")
    return backup_file

# Set up gzip
def gzip(backup_file_path):
    try:
        logger.info('Starting gzip')
        gzip_options = '-f ' + backup_file_path
        subprocess.check_call([gzip, gzip_options], shell=False)
        logger.info('Gzip completed')
    except subprocess.CalledProcessError as e:
        logger.error('Gzip failed')
        sys.exit(1)

# Set up Google Drive API

def get_authenticated_service(creds_path):
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

# Set up upload to Google Drive

def upload_file(service, file_path, folder_id=None):
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
       file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path,
                            resumable=True)
    
    try:
        file = service.files().create(
            supportsAllDrives=True,
	    body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        #print(f'File ID: {file.get("id")}')
    except Exception as e:
        print(f'Error uploading file: {str(e)}')


if __name__ == "__main__":
    container_name = "digifolk_db_1"
    backup_file=backup(container_name)
#    gzip(backup_file)
    
    FOLDER_ID = '1ixhPAFmRx_7xNGhxEEE3onNjGW6WPC7z'  # Replace with the ID of the destination folder in your Google Drive
    CREDENTIALS_FILE = '/home/marianavarro/digifolk-master/digifolk/GD-digifolk.json'
    service = get_authenticated_service(CREDENTIALS_FILE)
    files_to_upload = glob.glob('/home/marianavarro/backup/digifolk_db_1_backup_*.sql')  # Replace the pattern as needed
    for file_to_upload in files_to_upload:
        upload_file(service, file_to_upload, FOLDER_ID)
        os.remove(file_to_upload)
    
 


# Set up cron
# crontab -e
# 0 0 * * * /usr/bin/python3 /home/backup.py
# 0 0 * * * /bin/rm -f /home/backup/backup.sql.gz

# Set up logrotate
# /etc/logrotate.d/backup
# /var/log/backup.log {
#     rotate 7
#     daily
#     compress
#     delaycompress
#     missingok
#     notifempty
#     create 644 root root
#     sharedscripts
#     postrotate
#         /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true
#     endscript
# }



