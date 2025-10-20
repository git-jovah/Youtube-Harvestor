import streamlit as st,pandas as pd,main
from main import wanted_data_gather,get_channel_info
import numpy as np

st.set_page_config("youtube harvester",layout="wide")
channel_list = set()

if "selected_channel" not in st.session_state:
    st.session_state.selected_channel = None
if "selected_playlist" not in st.session_state:
    st.session_state.selected_playlist = None
if "selected_video" not in st.session_state:
    st.session_state.selected_video = None

h1,_,h2 = st.columns([0.7,0.7,0.1])
h1.title(":red[YOU]TUBE HARVESTER",anchor=False)
if h2.button("?",help="help"):
    st.toast("""Application Guide:      
                1. It harvestes data using channel names.   
                2. The channel should be active.    
                3. The channel should contain at least one playlist.    
                4. It collects all the data from a channel.     
            """,duration="short")
search =  st.text_input('Enter channels:',placeholder="Channel names(apple,Tseries,...)",)
# if st.button("search",use_container_width=True):
st.write("channels : ")
ssl = set(search.split(","))
a = st.columns([0.3]*len(ssl))
c1,c2,c3 = st.columns([0.3,0.3,0.3])


if search:
    # main.get_channel_columns(search)
    for x,channel in enumerate(ssl):
        channel = channel.strip()
        # if a[x].button(channel,use_container_width=True,key=f"{channel}"):
        if a[x].checkbox(channel):
            if main.channel_exist(channel):
                st.session_state.selected_channel = channel
                st.success(channel)
                channel_list.add(channel)

            elif main.channel_exist_by_name(channel):
                st.session_state.selected_channel = channel
                st.success(channel)
                channel_list.add(channel)
            else:
                st.warning("channel does not exist!")
                st.session_state.selected_channel = None

if len(channel_list)<=1:
    if channel := st.session_state.selected_channel:
        channel_id = main.get_channel_id_by_handle(channel) if (channel[0] == '@') else main.get_channel_id_by_username(channel)
        if get_channel_info(channel_id):
            playlist_names = main.DATA_POOL["playlist_details"]["playlist_name"]
            selected_playlist = c1.selectbox(
                "select playlist",
                options=playlist_names,
                index=playlist_names.index(st.session_state.selected_playlist) if st.session_state.selected_playlist in playlist_names else 0
                )
            video_count = c2.number_input("videos from playlist",max_value=10 if main.playlistitems_results <= 3 else main.playlistitems_results,min_value=3)
            st.write()
            st.write("-"*50)
            st.markdown(":red[Table] : channel")
            data = main.DATA_POOL["channel_details"]
            df = pd.DataFrame(data,columns = data.keys())
            df.drop("channel_description",axis=1,inplace=True)
            st.table(df)

        if any(df := pd.DataFrame(main.DATA_POOL['playlist_details'],columns=main.DATA_POOL["playlist_details"].keys(),index=[i for i in range(0,len(main.DATA_POOL["playlist_details"]["playlist_name"]))])):
            st.write()
            st.write("-"*50)
            st.markdown(":red[Table] : playlists")
            st.table(df)
        else:
            st.write()
            st.write("-"*50)
            st.markdown(":red[Table] : playlists")
            st.error("No playlists found !")
        if selected_playlist:
            temp_map = dict(zip(main.DATA_POOL["playlist_details"]["playlist_name"],main.DATA_POOL["playlist_details"]["playlist_id"]))
            main.get_playlistItems(temp_map[selected_playlist],count = video_count)
            
            item_names = main.DATA_POOL['playlist_items'].get("item_name", [])
            selected_video = c3.selectbox("Select video",options=item_names,
            index=item_names.index(st.session_state.selected_video) if st.session_state.selected_video in item_names else 0 if item_names else None,
            )
            
            st.session_state.selected_video = selected_video
            data = main.DATA_POOL["playlist_items"]
            if any(df := pd.DataFrame(data,columns=data.keys())):
                st.write()
                st.write("-"*50)
                st.markdown(":red[Table] : Playlist Items")
                st.table(df)
            else:
                st.write()
                st.write("-"*50)
                st.markdown(":red[Table] : Playlist Items")
                st.error("No playlist items found !")
            pdet = main.DATA_POOL["playlist_items"]
            temp_video_map = dict(zip(pdet['item_name'],pdet['item_id']))
            if selected_video:
                main.get_video_details(temp_video_map[selected_video])
                data = main.DATA_POOL["video_details"]
                data.pop("video_description")
                st.write()
                st.write("-"*50)
                st.write(":red[Table] : video details")
                st.table(data)
                # if any(df := pd.DataFrame(data,columns=data.keys(),index=[0])):
                #     st.write()
                #     st.write("-"*50)
                #     st.table(df)
                # else:
                #     st.write()
                #     st.write("-"*50)
                #     st.warning("no video details found")
        st.write(main.DATA_POOL)

elif len(channel_list) > 1:
    channel_details_dict = {}
    playlist_details_dict = {}
    data = dict()
    for channel in channel_list:
        channel_id = main.get_channel_id_by_handle(channel) if (channel[0] == '@') else main.get_channel_id_by_username(channel)
        if get_channel_info(channel_id):
            ch_det = main.DATA_POOL["channel_details"]
            pl_det = main.DATA_POOL["playlist_details"]
            channel_details_dict[channel] = ch_det
            playlist_details_dict[channel] = pl_det
    # st.write(channel_details_dict)
    # st.write(playlist_details_dict)
    df1 = pd.DataFrame(channel_details_dict[list(channel_list)[0]])
    st.table(df1)
    
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH
    # THERE IS ERROR OCCURING ABIUT THE ARRAY NOT BEING SAME LENGTH

    df2 = pd.DataFrame(channel_details_dict[list(channel_list)[1]])
    # st.table(df2)
    # st.table(df1.merge(df2,on=list(df.columns),how="outer"))
    # st.write(data)
    if data:
        df1 = pd.DataFrame(data[list(data.keys())[0]],columns=data[list(data.keys())[0]].keys())
        # df2 = pd.DataFrame(data[list(data.keys())[1]],columns=data[list(data.keys())[1]].keys())
        # df1.merge(df2,on="")
        st.table(df1)


