from azure.storage.blob import ContainerClient

''' script for listing names of songs preset in azure data storage '''

# Regular blob listing
def list_blobs_flat_listing():
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=mashups;AccountKey=b1o2WbRLU1fyBPNUdUAH7usYrBINuw2WzfxFaOzq9/egfDG1t1+GYV2QdCQXBFoK4Tpg5ZIWtL6BKKpbviGg4A==;EndpointSuffix=core.windows.net'

    container_client = ContainerClient.from_connection_string(connect_str, container_name="mashups")

    # List blobs in the specified container
    songs_list_blob = []
    blobs_list = container_client.list_blobs()
    for blob in blobs_list:
        if blob.name.startswith('songs/') and blob.name != 'mixed_songs' and blob.name != 'songs':
            print('Blob: ' + blob.name)
            songs_list_blob.append(blob.name)
    return songs_list_blob
