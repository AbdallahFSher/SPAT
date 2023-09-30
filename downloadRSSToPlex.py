import feedparser
import requests
import string
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from io import BytesIO
import os
import subprocess

# Replace with your RSS feed URL
rss_feed_url = ''

# Replace with the path to your Plex server's podcast directory
plex_podcast_dir = ''

# Replace with the path to mp3val.exe on your computer
mp3val_path = ''

# Define a set of valid characters for filenames
valid_chars = f'-_.() {string.ascii_letters}{string.digits}'

feed = feedparser.parse(rss_feed_url)

for entry in feed.entries:
    # Get the URL of the mp3 file from the enclosure tag
    mp3_url = entry.enclosures[0].href

    # Use the title of the podcast episode as the filename and remove any invalid characters
    filename = f'{entry.title}.mp3'
    filename = ''.join(c for c in filename if c in valid_chars)

    # Check if the file already exists in the Plex podcast directory before downloading it
    
    filepath = f'{plex_podcast_dir}/{filename}'
    
    if not os.path.exists(filepath):
        response = requests.get(mp3_url)
        with open(filepath, 'wb') as f:
            f.write(response.content)

        # Edit the metadata of the mp3 file using mutagen
        
        audio = EasyID3(filepath)
        
        audio['title'] = entry.title
        
        audio.save()
        
        # Add an album cover to the mp3 file using mutagen
        
        if hasattr(entry, 'image'):
            image_url = entry.image.href
            
            response = requests.get(image_url)
            
            image_data = BytesIO(response.content)
            
            audio = ID3(filepath)

            audio.add(
                APIC(
                    encoding=0,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=image_data.read()
                )
            )
            
            audio.save()

# Run mp3val to check for corruption in downloaded files

subprocess.run([mp3val_path, f'{plex_podcast_dir}/*.mp3', '-f', '-t'])
