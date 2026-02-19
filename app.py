import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import src
import plotly.express as px
import plotly.figure_factory as ff
import database as db

st.set_page_config("YouTube Harvester", layout="wide")
st.title(":red[YOU]TUBE HARVESTER")

if "selected_channels" not in st.session_state:
    st.session_state.selected_channels = []
if "selected_playlist" not in st.session_state:
    st.session_state.selected_playlist = None
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None

_, help_col, _ = st.columns([0.8, 0.1, 0.1])
if help_col.button("?", help="Click for help"):
    st.toast("""Application Guide:  
1. Enter one or more channels separated by comma.   
2. The channel should be active.    
3. Select channels to fetch details.    
4. View playlists and video details in tables.  
5. Compare multiple channels via graphs.
""", duration="short")

search_input = st.text_input("Enter channel handles or usernames (comma separated):", placeholder="@apple,@Tseries,...")
selected_channels = []

if search_input:
    channels_input = set([c.strip() for c in search_input.split(",")])
    st.write("Select channels to fetch details:")
    checkboxes = st.columns([0.2] * len(channels_input))
    for i, channel in enumerate(channels_input):
        if checkboxes[i].checkbox(channel):
            selected_channels.append(channel)

st.session_state.selected_channels = selected_channels

c1,c2 = st.columns([0.5,0.5])
if not selected_channels:
    st.info("Please select at least one channel above.")
    st.stop()

channels_data = []
for ch in st.session_state.selected_channels:
    data = asyncio.run(src.get_channel_info(ch))
    if data:
        channels_data.append({
            "channel_id": data["channel_id"][0],
            "channel_name": data["channel_name"][0],
            "channel_views": data["views"][0],
            "channel_subscriberCount": data["subscribers"][0],
            "channel_videos": data["videos"][0],
            "channel_description": data["description"][0],
            "channel_status": data["status"][0]
        })

if not channels_data:
    st.error("Channel info not found!")
    st.stop()

channels_df = pd.DataFrame(channels_data)
# Convert numeric columns
for col in ["channel_views", "channel_subscriberCount", "channel_videos"]:
    channels_df[col] = pd.to_numeric(channels_df[col], errors="coerce").fillna(0)

st.divider()
st.subheader(":red[Table] : Channels")
st.dataframe(channels_df, use_container_width=True)

st.divider()
st.subheader(":red[Graphs] : Channels Comparison")

fig1 = px.bar(channels_df, x="channel_name", y="channel_subscriberCount", title="Subscribers by Channel")
fig2 = px.bar(channels_df, x="channel_name", y="channel_videos", title="Videos Count by Channel")
fig3 = px.bar(channels_df, x="channel_name", y="channel_views", title="Total Views by Channel")

graph_col1, graph_col2, graph_col3 = st.columns([0.3, 0.3, 0.3])
graph_col1.plotly_chart(fig1, use_container_width=True)
graph_col2.plotly_chart(fig2, use_container_width=True)
graph_col3.plotly_chart(fig3, use_container_width=True)

# 2D Density Plots
fig4 = ff.create_2d_density(x=channels_df["channel_views"], y=channels_df["channel_subscriberCount"], title="Views vs Subscribers")
fig5 = ff.create_2d_density(x=channels_df["channel_views"], y=channels_df["channel_videos"], title="Views vs Videos")
fig6 = ff.create_2d_density(x=channels_df["channel_subscriberCount"], y=channels_df["channel_videos"], title="Subscribers vs Videos")

st.plotly_chart(fig4)
st.plotly_chart(fig5)
st.plotly_chart(fig6)

if len(st.session_state.selected_channels) == 1:
    channel_id = channels_df["channel_id"].iloc[0]

    @st.cache_data
    def fetch_playlists(cid):
        return asyncio.run(src.get_playlists(cid))

    playlists = fetch_playlists(channel_id)
    pl_df = pd.DataFrame(playlists)

    st.divider()
    st.subheader(":red[Table] : Playlists")
    if not pl_df.empty:
        st.dataframe(pl_df, use_container_width=True)

        selected_playlist = c1.selectbox("Select Playlist", pl_df["playlist_name"])
        playlist_id = pl_df.loc[pl_df["playlist_name"] == selected_playlist, "playlist_id"].values[0]

        @st.cache_data
        def fetch_videos(pid):
            return asyncio.run(src.get_playlist_items(pid))

        videos = fetch_videos(playlist_id)
        vid_df = pd.DataFrame(videos)
        st.divider()
        st.subheader(f":red[Table] : '{selected_playlist}' Items")
        st.dataframe(vid_df, use_container_width=True)

        selected_video = c2.selectbox("Select Video", vid_df["video_title"])
        video_id = vid_df.loc[vid_df["video_title"] == selected_video, "video_id"].values[0]

        @st.cache_data
        def fetch_video_details(vid_id):
            return asyncio.run(src.get_video_details(vid_id))

        video_details = fetch_video_details(video_id)
        st.divider()
        st.subheader(f":red[Table] : '{selected_video}' Details")
        st.dataframe(pd.DataFrame([video_details]), use_container_width=True)

_, upload_col, _ = st.columns([0.4, 0.2, 0.4])
if upload_col.button("Upload to Database", use_container_width=True):
    with st.spinner("Uploading data to database..."):
        success = db.db_run(channels_df, pl_df if 'pl_df' in locals() else None, vid_df if 'vid_df' in locals() else None)
        if success:
            st.success("Data uploaded successfully!")
            st.balloons()
        else:
            st.error("Failed to upload data.")
