import io
import os.path
import pathlib
from urllib.request import urlopen
import re
from pathlib import Path

''' script for connection with azure data storage and downloading files from it '''

''' function to download songs from songs directory - to mix them '''
def download_blob(name, path):
    url ='https://mashups.blob.core.windows.net/mashups/' + name.replace(' ', '%20')
    to_bytes = io.BytesIO(urlopen(url).read())
    name_song = name[6:]
    path_to_file = os.path.join(path, name_song)
    pathlib.Path(path_to_file).write_bytes(to_bytes.getbuffer())
    return path_to_file

''' function to download songs from mixed_songs directory - mixed ones - ready to stream '''
def download_blob_from_mixed(url, path):
    to_bytes = io.BytesIO(urlopen(url).read())
    name = re.search('https://mashups.blob.core.windows.net/mashups/mixed_songs/(.*).wav', url)
    name = name.group(1)
    name = name.replace('%20', ' ') + '.wav'
    path_to_file = os.path.join(path, name)
    pathlib.Path(path_to_file).write_bytes(to_bytes.getbuffer())
    return path_to_file

