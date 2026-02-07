from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
import csv

load_dotenv()
key = os.getenv("API_KEY")
youtube = build('youtube', 'v3', developerKey=key)
DATA_POOL = dict({})
playlistitems_results = 0

# def upload_to_db():
    # all playlist data
    # DATA_POOL["playlist_details"]
    # all vid data
    # DATA_POOL["video_details"]
    # with open("./tests/channel_data.csv","w",encoding="utf-8",newline="") as file:
    #     # selected channel data
    #     field_names =  DATA_POOL["channel_details"].keys()
    #     writer = csv.DictWriter(file,fieldnames=field_names)
    #     writer.writeheader()
    #     writer.writerow(DATA_POOL.get("channel_details"))

    # with open("./tests/playlist_data.csv","w") as file:
    #     field_names = DATA_POOL["playlist_details"].keys()
    #     writer = csv.DictWriter(file,fieldnames=field_names)
    #     writer.writeheader()
    #     writer.writerow(DATA_POOL["playlist_details"])

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
        "item_status": [],
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
        (playlist_items['item_name'].append(response["items"][i]["snippet"]["title"] ),
        playlist_items['item_id'].append(response["items"][i]["contentDetails"]["videoId"]),
        playlist_items['item_date'].append(response["items"][i]["contentDetails"]["videoPublishedAt"] if ("videoPubilshedAt" in response['items'][i]['contentDetails']) else None),
        playlist_items['item_status'].append(response['items'][i]['status']["privacyStatus"]) )
            for i in range(0,count)
        ]
    else:
        [
        (playlist_items['item_name'].append(response["items"][i]["snippet"]["title"] ),
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
        "video_duration" : [],
        'video_comments_count' : [],
        'video_commentText': [],
        "video_caption_status" : [],
        "video_thumbnail" : []
    }

    response = youtube.videos().list(
        part = "contentDetails,snippet,statistics,player,id,status,topicDetails,recordingDetails",
        id = video_id
    ).execute()
    # st.write(response)
    
        # extra_det["Likes"] = video['statistics'].get('likeCount', 'Hidden')
        # extra_det["Comments"] = video['statistics'].get('commentCount', 'Disabled')
    # assert response['items'] == None,"There are no items"
    video = response['items'][0] if any(response['items']) else None
    if video:
        video_details["video_name"]          .append(video["snippet"]['title'] if ("title" in  response["items"][0]['snippet'].keys()) else None)
        video_details["video_id"]            .append(video['id'])#if ("items" in  response["items"]) else None)
        video_details["video_date"]          .append(video['snippet']['publishedAt'] if ("publishedAt" in  response["items"][0]['snippet'].keys()) else None)
        video_details["video_description"]   .append(video['snippet']['description'] if ("description" in  response["items"][0]['snippet'].keys()) else None)
        video_details["video_views"]         .append(video['statistics']['viewCount'] if ("viewCount" in  response["items"][0]['statistics'].keys()) else None)
        video_details["video_likes"]         .append(video['statistics']['likeCount'] if ("likeCount" in  response["items"][0]['statistics'].keys()) else None)
        video_details["video_duration"]      .append(video['contentDetails']['duration'] if ("duration" in  response["items"][0]['contentDetails'].keys()) else None)
        try :
            video_details["video_comments_count"].append(video['statistics'].get("commentCount","disabled") )#if ("commentCounts" in  response["items"][0]['statistics'].keys()) else None)
        except:
            # video_details["video_comments_count"]= video['statistics']["commentCount"] if ("commentCounts" in  response["items"][0]['statistics'].keys()) else None
            video_details["video_comments_count"].append(0)
        video_details["video_caption_status"].append(video['contentDetails']['caption'] if ("caption" in  response["items"][0]['contentDetails'].keys()) else None)
        video_details["video_thumbnail"].append(video["snippet"]["thumbnails"]["standard"]["url"] if ("thumbnails" in  response["items"][0]['snippet'].keys()) else None)
        # st.write(video_details["video_comments_count"])
        if video_details["video_comments_count"][0] != "disabled":
            try:
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=5
                ).execute()
                text = ""
                for item in comments_response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    # st.write(f"- {comment['authorDisplayName']}: {comment['textDisplay'][:80]}...")
                    text+=(comment['authorDisplayName']+"-->"+comment["textDisplay"]+"  \n   ")
                video_details["video_commentText"].append(text)
            except:
                DATA_POOL['video_commentText'].append("NO COMMENTS")
        else:
            video_details['video_commentText'].append("NO COMMENTS")
        DATA_POOL['video_details'] = video_details
    else:
        video_details["video_name"]          = 0
        video_details["video_id"]            = 0
        video_details["video_date"]          = 0
        video_details["video_description"]   = 0
        video_details["video_views"]         = 0
        video_details["video_likes"]         = 0
        video_details["video_dislikes"]      = 0
        video_details["video_duration"]      = 0
        video_details["video_comments_count"]= 0
        video_details["video_caption_status"]= 0
        video_details["video_thumbnail"]     = 0
        video_details["video_commentText"]   = 0
        DATA_POOL["video_details"] = video_details
    # st.write(video_id)

def get_channel_info(ch,n=1): # n is temp for channel conunt
    # channel_id = get_channel_id_by_username(ch)
    channel_details = {
        "channel_id":[],
        "channel_name":[],
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
            if n==10:
                channel_details["channel_id"]                = response['items'][0]["id"]
                channel_details["channel_name"]              = response['items'][0]["snippet"]["title"]
                channel_details["channel_views"]             = response['items'][0]['statistics']['viewCount']
                channel_details["channel_videos"]            = response['items'][0]['statistics']['videoCount']
                channel_details["channel_subscriberCount"]   = response['items'][0]['statistics']['subscriberCount']
                channel_details["channel_description"]       = response['items'][0]["snippet"]["description"]
                channel_details["channel_status"]            = response['items'][0]['status']['privacyStatus']
            else:
                channel_details["channel_id"].append(response['items'][0]["id"])
                channel_details["channel_name"].append(response['items'][0]["snippet"]["title"])
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


def get_every_video_from_playlists(channel: str | None = None) -> pd.DataFrame:
    '''
    Gets every video details from the playlists.
    
    :TODO
    this function depends on atleast one execution of the get_video_details() func. change soon
    
    '''
    if ((channel == None) or (channel!=None)) and any(DATA_POOL['channel_details']):
        allvid_df = pd.DataFrame(DATA_POOL["video_details"])
        playlistData = list(DATA_POOL["playlist_details"]["playlist_id"])
        for _playlist in playlistData:
            # st.write(f"--{_playlist}")
            get_playlistItems(_playlist,count=30)
            playlistItemData =  list(DATA_POOL["playlist_items"]["item_id"])
            pl =  list(DATA_POOL["playlist_items"]["item_name"])
            a = dict(zip(pl,playlistItemData))
            # st.write(a)
            for _item in playlistItemData:
                pass
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # st.write(f'{x} - {_item}')
                # get_video_details(_item)
                # t1 = pd.DataFrame(DATA_POOL["video_details"])
                # allvid_df = allvid_df.merge(t1,how="outer")
        return allvid_df
    else:
        get_channel_info(channel)
        return get_every_video_from_playlists()
 
def get_every_video_in_playlist(playlistId: str | None = None) -> pd.DataFrame:
    """
    returns DataFrame that consits of all videos info in a playlist
    
    :TODO
    this function depends on atleast one execution of the get_video_details() func. change soon
    
    """

    if any(sc_data:=DATA_POOL["video_details"]) and (playlistId != None):
        video_data = pd.DataFrame(sc_data)
        for pl_item in DATA_POOL["playlist_items"]["item_id"]:
            get_video_details(pl_item)
            temp_sc = pd.DataFrame(DATA_POOL["video_details"])
            video_data = video_data.merge(temp_sc,how="outer")
        # st.table(video_data)
        return video_data

if __name__ == '__main__':
    print("running main file")
    