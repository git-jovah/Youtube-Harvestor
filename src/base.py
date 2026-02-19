import os
import asyncio
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

DATA_POOL = {}


async def get_channel_info(channel: str):
    """Fetch channel info by handle (@) or username"""
    async def _fetch_by_username(username):
        return await asyncio.to_thread(lambda: youtube.channels().list(
            part="snippet,statistics,status",
            forUsername=username
        ).execute())

    async def _fetch_by_handle(handle):
        return await asyncio.to_thread(lambda: youtube.channels().list(
            part="snippet,statistics,status",
            forHandle=handle
        ).execute())

    response = None
    if channel.startswith("@"):
        response = await _fetch_by_handle(channel)
    else:
        response = await _fetch_by_username(channel)

    if not response.get("items"):
        return None

    item = response["items"][0]

    DATA_POOL["channel_details"] = {
        "channel_id": [item["id"]],
        "channel_name": [item["snippet"]["title"]],
        "views": [int(item["statistics"].get("viewCount", 0))],
        "subscribers": [int(item["statistics"].get("subscriberCount", 0))],
        "videos": [int(item["statistics"].get("videoCount", 0))],
        "description": [item["snippet"].get("description", "")],
        "status": [item.get("status", {}).get("privacyStatus", "public")]
    }
    return DATA_POOL["channel_details"]

async def get_playlists(channel_id: str):
    def fetch():
        return youtube.playlists().list(
            part="snippet",
            channelId=channel_id,
            maxResults=25
        ).execute()
    response = await asyncio.to_thread(fetch)
    playlists = []
    for item in response.get("items", []):
        playlists.append({
            "playlist_id": item["id"],
            "playlist_name": item["snippet"]["title"],
            "playlist_date": item["snippet"].get("publishedAt", "")
        })
    DATA_POOL["playlists"] = playlists
    return playlists

async def get_playlist_items(playlist_id: str):
    def fetch():
        return youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        ).execute()
    response = await asyncio.to_thread(fetch)
    items = []
    for i in response.get("items", []):
        items.append({
            "video_id": i["contentDetails"]["videoId"],
            "video_title": i["snippet"]["title"],
            "video_date": i["snippet"].get("publishedAt", ""),
            "status": i.get("status", {}).get("privacyStatus", "public")
        })
    DATA_POOL["playlist_items"] = items
    return items

async def get_video_details(video_id: str):
    def fetch():
        return youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
    response = await asyncio.to_thread(fetch)
    if not response.get("items"):
        return None

    v = response["items"][0]
    details = {
        "video_id": v["id"],
        "title": v["snippet"].get("title",""),
        "description": v["snippet"].get("description",""),
        "views": int(v["statistics"].get("viewCount", 0)),
        "likes": int(v["statistics"].get("likeCount", 0)),
        "duration": v["contentDetails"].get("duration", ""),
        "comments_count": int(v["statistics"].get("commentCount", 0))
    }

    DATA_POOL.setdefault("video_details", []).append(details)
    return details
