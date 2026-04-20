import requests as rs
import json 
import os
from dotenv import load_dotenv
from datetime import date

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

def batch_list(video_id_list, batch_size):
    # range(start, stop, step)
    for i in range(0, len(video_id_list), batch_size):
        yield video_id_list[i : i + batch_size]




def extract_video_data(video_ids):
    extracted_data = []
    def batch_list(video_id_list, batch_size):
    # range(start, stop, step)
        for i in range(0, len(video_id_list), batch_size):
            yield video_id_list[i : i + batch_size]
            '''
            This is the "magic" word. Instead of creating a new giant list of lists (which eats up memory), 
            yield returns one chunk at a time and "pauses" the function. The next time you ask for a chunk, it picks up exactly where it left off.
            '''

    try:
        for batch in batch_list(video_ids, max_Results):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            response = rs.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id" : video_id,
                    "title" : snippet['title'],
                    "publishedAt" :snippet["publishedAt"],
                    "duration" : contentDetails["duration"],
                    "viewCount" : statistics.get('viewCount', None),
                    "likeCount" : statistics.get('likeCount', None),
                    "commentCount" : statistics.get('commentCount', None)
                }
                
                extracted_data.append(video_data)

        return extracted_data

    except rs.exceptions.RequestException as e :
        raise e 
    
'''
### The Breakdown
* **`data`**: The Python dictionary you want to save.
* **`f`**: The open file object (your destination).
* **`indent=4`**: This is optional but highly recommended for Data Engineers. It makes the file "pretty" and readable by adding spaces and line breaks.
Without it, the whole JSON would be one giant, messy line.
'''

'''
### `json.dump()` vs `json.dumps()`
This is the most common point of confusion for developers. Note the extra **"s"**:

| Function | What it does | Result |
| :--- | :--- | :--- |
| **`json.dump()`** | Dumps data into a **file**. | A `.json` file on your disk. |
| **`json.dumps()`** | Dumps data into a **string**. | A text variable in your code. |

**Pro-Tip for your Project:**
When you are extracting 800+ videos from MrBeast's channel, you don't want to keep them all in your computer's RAM.
Using `json.dump()` to save each batch to a local folder ensures that if your script crashes halfway through,
you haven't lost the data you already spent your API quota to get! 
'''   


def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"

    with open(file_path, 'w', encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4,  ensure_ascii=False)


if __name__ == "__main__":
    playlist_id = get_playlistId()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)

    
        

