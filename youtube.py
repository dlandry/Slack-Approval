from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from oauth2client.tools import argparser
from datetime import datetime, timedelta
import urllib.request
import json
import os
import isodate
 

# Set API key and build YouTube service
# API_KEY = 'AIzaSyBtxL4zudwYcFHOAROo953Q_U3HTcTXf8E'
API_KEY = 'AIzaSyDAuo9wXO5tdQPx3GOcj41k-MZqe3bfZiA'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)


def download_transcript(video_id):
    api_key = 'AIzaSyDAuo9wXO5tdQPx3GOcj41k-MZqe3bfZiA'  # Replace with your own API key
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Save the transcript into a JSON file with the video_id as the file name
    with open(f"{video_id}.json", "w") as f:
        json.dump(transcript, f)

    print("Transcript downloaded successfully.")



def download_thumbnail(video_id):
    api_key = 'AIzaSyDAuo9wXO5tdQPx3GOcj41k-MZqe3bfZiA' # Replace with your own API key

    # Construct the URL to fetch video details including thumbnail
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet&key={api_key}"

    try:
        # Fetch video details from the YouTube Data API
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # Get the URL of the thumbnail image
        thumbnail_url = data['items'][0]['snippet']['thumbnails']['default']['url']

        # Download the thumbnail image
        urllib.request.urlretrieve(thumbnail_url, f"{video_id}_thumbnail.jpg")
        print("Thumbnail downloaded successfully.")
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
        


# Define the search query parameters
query = 'science'
published_after = (datetime.now() - timedelta(days=1)).isoformat() + 'Z'  # Videos published from today till now

# Call the search.list method to get the matching videos
try:
    search_response = youtube.search().list(
        q=query,
        part='id',
        type='video',
        order='viewCount',
        maxResults=10,
        publishedAfter=published_after
    ).execute()

    # Retrieve the video IDs from the search results
    video_ids = []

    for item in search_response.get('items', []):
        video_id = item['id']['videoId']
        video_detail_response = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        ).execute()

        content_details = video_detail_response.get('items', [])[0]['contentDetails']
        duration = isodate.parse_duration(content_details['duration'])
        captions_response = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        has_english_transcript = False

        for caption_item in captions_response.get('items', []):
            caption_language = caption_item['snippet']['language']
            if caption_language == 'en':
                has_english_transcript = True
                break

        if duration.total_seconds() > 90 and has_english_transcript:
            video_ids.append(video_id)
            

    # for video_id in video_ids:
    #     os.mkdir(video_id)
    #     os.chdir(video_id)
    #     print(video_id)
    #     # download_thumbnail(video_id)
    #     download_transcript(video_id)
    #     os.chdir("./..")

except Exception as e:
    print(f"Error during search: {e}")

    # Display the video IDs
for video_id in video_ids:
    print("https://www.youtube.com/watch?v=" + video_id)
    try:
            os.mkdir(video_id)
            os.chdir(video_id)
            print(f"Directory {video_id} created and set as current directory.")
            download_thumbnail(video_id)
            # YouTubeTranscriptApi.get_transcript(video_id)
            download_transcript(video_id)
            os.chdir("./..")
    except Exception as e:
            print(f"Error creating directory: {e}")