import requests as rs
import json 
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("API_KEY")
max_Results = 50
CHANNEL_HANDLE = "MrBeast"



def get_playlistId():

    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"
    try:
        response = rs.get(url)
        response.raise_for_status()
        data = response.json()
        channel_items = data['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlistId
    except rs.exceptions.RequestException as e:
        raise e





'''
def get_video_ids(playlist_id):
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_Results}&playlistId={playlist_id}&key={API_KEY}"
    video_ids = []
    page_token = None
    
    try:
        while True:
            if page_token:
                url = base_url + f"&pageToken={page_token}"
                response = rs.get(url)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    video_id = item['contentDetails']['videoId']
                    video_ids.append(video_id)

                page_token = data.get('nextPageToken')
                
                if not page_token:
                    break

        return video_ids

    except rs.exceptions.RequestException as e:
        raise e
'''
def get_video_ids(playlist_id):
    base_url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    video_ids = []
    page_token = None
    
    try:
        while True:
            # Build params dynamically
            params = {
                'part': 'contentDetails',
                'maxResults': max_Results,
                'playlistId': playlist_id,
                'key': API_KEY,
                'pageToken': page_token  # requests handles None by ignoring it
            }
            
            response = rs.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("items", []):
                video_ids.append(item['contentDetails']['videoId'])

            page_token = data.get('nextPageToken')
            
            # Print progress (Good for Data Engineering logs)
            print(f"Fetched {len(video_ids)} IDs so far...")

            if not page_token:
                break
                
        return video_ids

    except rs.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise e

if __name__ == "__main__":
    playlist_id = get_playlistId()
    print(get_video_ids(playlist_id))

    
        

