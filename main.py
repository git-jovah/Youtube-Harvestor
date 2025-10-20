from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
key = os.getenv("API_KEY")
youtube = build('youtube', 'v3', developerKey=key)
DATA_POOL = dict({})
playlistitems_results = 0

def channel_exist(c):
    response = youtube.channels().list(
        part = 'id',
        forHandle = c,
    ).execute()
    return True if response['pageInfo']['totalResults'] > 0 else False

def channel_exist_by_name(c):
    response = youtube.channels().list(
        part = 'id',
        forUsername = c,
    ).execute()
    return True if response['pageInfo']['totalResults'] > 0 else False

def get_channel_id_by_username(username):
    request = youtube.channels().list(
        part='id',
        forUsername = username,
    )
    response = request.execute()
    try:
        if response['items']:
            print("channel info :")
            print(response['items'])
            return response['items'][0]['id']
    except:
        st.warning("something went wrong when searching for name")
        
def get_channel_id_by_handle(handle):
    response = youtube.channels().list(
        part = 'id',
        forHandle = handle
    ).execute()
    try :
        if response['items']:
            print('channel info :')
            print(response['items'])
            return response['items'][0]['id']
    except:
        st.warning('something went wrong')
def get_video_id_by_name(n):
    request = youtube.search().list(
        part = "snippet",
        q = n,
        type="video",
        maxResults = 1
    )

    response = request.execute()
    if response['items']:
        for res in response["items"]:
            return res['id']['videoId']

def wanted_data_gather(search):
    video_id = get_video_id_by_name(search)

    youtube = build('youtube', 'v3', developerKey=key)

    video_response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()
    if video_response['items']:
        video = video_response['items'][0]
        DATA_POOL["**Title**"] = video['snippet']['title']
        DATA_POOL["**Channel**"] = video['snippet']['channelTitle']
        DATA_POOL["**Views**"]  = video['statistics']['viewCount']
        DATA_POOL["**Likes**"] = video['statistics'].get('likeCount', 'Hidden')
        DATA_POOL["**Comments**"] = video['statistics'].get('commentCount', 'Disabled')

    comments_response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=5
    ).execute()

    st.markdown("\nTop Comments:")
    text = ""
    for item in comments_response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        # st.write(f"- {comment['authorDisplayName']}: {comment['textDisplay'][:80]}...")
        text+=(comment['authorDisplayName']+"-"+comment["textDisplay"][:30]+"..."+"  \n   ")
    DATA_POOL["comment text"] = text

def get_playlists(ch):
    """ for getting playlists"""
    count = 10
    playlist_details = {"playlist_name":[],
                        "playlist_id":[],
                        "playlist_date":[]
                        }
    response = youtube.playlists().list(
        part = "snippet,contentDetails",
        channelId = ch,
        maxResults = count
    ).execute()
    if response['pageInfo']['totalResults'] >= count:
        [
            (playlist_details['playlist_name'].append(response["items"][i]["snippet"]['title']),
            playlist_details['playlist_id'].append(response["items"][i]["id"]),
            playlist_details['playlist_date'].append(response["items"][i]["snippet"]['publishedAt']))
            for i in range(0,count)
        ]
    else:
        [
            (playlist_details['playlist_name'].append(response["items"][i]["snippet"]['title']),
            playlist_details['playlist_id'].append(response["items"][i]["id"]),
            playlist_details['playlist_date'].append(response["items"][i]["snippet"]['publishedAt']))
            for i in range(0,response['pageInfo']['totalResults'])
        ]

    # st.write(response.get('items'))
    DATA_POOL["playlist_details"]=playlist_details

def get_playlistItems(playlist_id,count = 3):
    """ for getting playlists items"""
    global playlistitems_results
    playlist_items = {
        "item_name" : [],
        "item_id"   : [],
        "item_date" : [],
        "item_status"    : [],

    }

    response = youtube.playlistItems().list(
        part = 'id,snippet,contentDetails,status',
        playlistId = playlist_id,
        maxResults = count
    ).execute()
    # st.write(playlist_id)
    # st.write(response)
    playlistitems_results = response['pageInfo']['totalResults']
    if response['pageInfo']['totalResults'] >= count:
        [
        (playlist_items['item_name'].append(response["items"][i]["snippet"]["title"]),
        playlist_items['item_id'].append(response["items"][i]["contentDetails"]["videoId"]),
        playlist_items['item_date'].append(response["items"][i]["contentDetails"]["videoPublishedAt"] if ("videoPubilshedAt" in response['items'][i]['contentDetails']) else None),
        playlist_items['item_status'].append(response['items'][i]['status']["privacyStatus"]) )
            for i in range(0,count)
        ]
    else:
        [
        (playlist_items['item_name'].append(response["items"][i]["snippet"]["title"]),
        playlist_items['item_id'].append(response["items"][i]["contentDetails"]["videoId"]),
        playlist_items['item_date'].append(response["items"][i]["contentDetails"]["videoPublishedAt"] if ("videoPubilshedAt" in response['items'][i]['contentDetails']) else None),
        playlist_items['item_status'].append(response['items'][i]['status']["privacyStatus"]) )
            for i in range(0,response['pageInfo']['totalResults'])
        ]
        ...

    # st.write(response['items'])
    DATA_POOL["playlist_items"] = playlist_items

# def get_channel_columns(chid):
#     st.write(get_channel_id_by_username(chid))
#     response = youtube.channelSections().list(
#         part = "snippet,id",
#         id = get_channel_id_by_username(chid)
#     ).execute()
#     st.write(response)

def get_video_details(video_id):
    "gives the video details"
    video_details = {
        "video_name" : [],
        "video_id"   : [],
        "video_date" : [],
        "video_description" : [],
        "video_views" : [],
        "video_likes" : [],
        # "video_dislikes" : [],
        "video_duration" : [],
        'video_comments_count' : [],
        "video_caption_status" : [],
        "video_thumbnail" : []
    }

    response = youtube.videos().list(
        part = "contentDetails,snippet,statistics,player,id,status,topicDetails,recordingDetails",
        id = video_id
    ).execute()
    # st.write(response)
    if response['items']:
        video_details["video_name"]          = response["items"][0]["snippet"]['title'] if ("title" in  response["items"][0]['snippet'].keys()) else None
        video_details["video_id"]            = response['items'][0]['id'] if ("items" in  response["items"]) else None
        video_details["video_date"]          = response['items'][0]['snippet']['publishedAt'] if ("publishedAt" in  response["items"][0]['snippet'].keys()) else None
        video_details["video_description"]   = response['items'][0]['snippet']['description'] if ("description" in  response["items"][0]['snippet'].keys()) else None
        video_details["video_views"]         = response["items"][0]['statistics']['viewCount'] if ("viewCount" in  response["items"][0]['statistics'].keys()) else None
        video_details["video_likes"]         = response["items"][0]['statistics']['likeCount'] if ("likeCount" in  response["items"][0]['statistics'].keys()) else None
        # video_details["video_dislikes"]    = response[][0][][]
        video_details["video_duration"]      = response["items"][0]['contentDetails']['duration'] if ("duration" in  response["items"][0]['contentDetails'].keys()) else None
        video_details["video_comments_count"]= response['items'][0]['statistics']["commentCounts"] if ("commentCounts" in  response["items"][0]['statistics'].keys()) else None
        video_details["video_caption_status"]= response["items"][0]['contentDetails']['caption'] if ("caption" in  response["items"][0]['contentDetails'].keys()) else None
        video_details["video_thumbnail"]     = response["items"][0]["snippet"]["thumbnails"]["standard"]["url"] if ("thumbnails" in  response["items"][0]['snippet'].keys()) else None
        DATA_POOL['video_details'] = video_details
    else:
        video_details["video_name"]          = None 
        video_details["video_id"]            = None
        video_details["video_date"]          = None
        video_details["video_description"]   = None
        video_details["video_views"]         = None
        video_details["video_likes"]         = None
        video_details["video_dislikes"]      = None
        video_details["video_duration"]      = None
        video_details["video_comments_count"]= None
        video_details["video_caption_status"]= None
        video_details["video_thumbnail"]     = None
        DATA_POOL["video_details"] = video_details
    # st.write(video_id)

def get_channel_info(ch):
    # channel_id = get_channel_id_by_username(ch)
    channel_details = {
        "channel_id":[],
        "channel_name":[],
        "channel_type" : [],
        "channel_views" : [],
        "channel_description" : [],
        "channel_videos":[],
        "channel_subscriberCount":[],
        "channel_status" : [],
    }
    response = youtube.channels().list(
        part="id,contentOwnerDetails,statistics,status,contentDetails,snippet,topicDetails",
        id=ch,
        # forUsername=ch
    ).execute()
    # st.write(response)
    # st.write("-"*10)
    try :
        if any(response["items"]):
            channel_details["channel_id"].append(response['items'][0]["id"])
            channel_details["channel_name"].append(response['items'][0]["snippet"]["title"])
            # channel_details["channel_type"].extend(response["items"][0]["topicDetails"]['topicCategories'])
            channel_details["channel_views"].append(response['items'][0]['statistics']['viewCount'])
            channel_details["channel_videos"].append(response['items'][0]['statistics']['videoCount'])
            channel_details["channel_subscriberCount"].append(response['items'][0]['statistics']['subscriberCount'])
            channel_details["channel_description"].append(response['items'][0]["snippet"]["description"])
            channel_details["channel_status"].append(response['items'][0]['status']['privacyStatus'])
        else:
            st.warning("no channel found")
    except Exception as e:
        st.warning(e)
        st.warning(f"no {e} found")
    get_playlists(ch)
    DATA_POOL["channel_details"] = channel_details
    return True

if __name__ == '__main__':
    # get_channel_id_by_username('Google')
    print("running main file")
    wanted_data_gather()