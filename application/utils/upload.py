import os
import magic
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings


def finfo(file):
    return magic.from_file(file, mime=True)


def upload_file(file_name,new_name):

    container_name = 'data'
    connection_string = os.environ['AZURE_CONNECTION_STRING']

    blob_client = BlobServiceClient.from_connection_string(connection_string)
    blob_obj = blob_client.get_blob_client(container=container_name,blob=new_name)

    with open(file_name,'rb') as file:
        blob_obj.upload_blob(file,overwrite=True,
            content_settings=ContentSettings(content_type=finfo(file_name),
                content_disposition=f'attachment; filename="{file_name}"'))

