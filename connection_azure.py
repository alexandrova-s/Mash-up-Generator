import os
import yaml
from azure.storage.blob import ContainerClient, ContentSettings

''' script for uploading files to azure data storage'''

def load_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    with open(dir_root + '/config.yaml', 'r') as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)


def get_files(dir):
    with os.scandir(dir) as entries:
        for entry in entries:
            if entry.is_file() and not entry.name.startswith('.'):
                yield entry


''' uploading files '''
def upload(files, connection_string, container_name):
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    print('Uploading files to blob storage...')

    for file in files:
        blob_client = container_client.get_blob_client(file.name)
        with open(file.path, 'rb') as data:
            my_content_settings = ContentSettings(content_type='audio/mpeg')
            blob_client.upload_blob(data, overwrite=True, content_settings=my_content_settings)
            # blob_client.upload_blob(data)
            print(f'{file.name} uploaded to blob storage')

