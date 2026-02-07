import streamlit as st,pandas as pd,main
from main import get_channel_info
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
                st.warning("channel does not exist or channel activity may not be irregular !")
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
            
            st.divider()
            st.markdown(":red[Table] : channel")
            data = main.DATA_POOL["channel_details"]
            df = pd.DataFrame(data,columns = data.keys())
            df.drop("channel_description",axis=1)
            # st.markdown(data)
            st.table(df)

        if any(df := pd.DataFrame(main.DATA_POOL['playlist_details'],columns=main.DATA_POOL["playlist_details"].keys(),index=[i for i in range(0,len(main.DATA_POOL["playlist_details"]["playlist_name"]))])):
            st.write()
            st.divider()
            st.markdown(":red[Table] : playlists")
            st.table(df)
        else:
            st.write()
            st.divider()
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
                st.divider()
                st.markdown(f":red[Table] : \"{selected_playlist}\" items")
                st.table(df)
            else:
                st.write()
                st.divider()
                st.markdown(f":red[Table] : \"{selected_playlist}\" items")
                st.error("No playlist items found !")
            pdet = main.DATA_POOL["playlist_items"]
            temp_video_map = dict(zip(pdet['item_name'],pdet['item_id']))
            if selected_video:
                main.get_video_details(temp_video_map[selected_video])
                
                total_videos = main.get_every_video_from_playlists(channel=channel)
                # st.table(total_videos)
                sc_data = main.DATA_POOL["video_details"]
                sc_data.pop("video_description")
                # wanted_data_gather(selected_video)
                # data = main.DATA_POOL["extra_det"]
                st.divider()
                st.write(f":red[Table] : \"{selected_video} \" details")
                st.table(sc_data)
                # main.get_video_details('rzX5m2UZXFo')
                # st.table(main.DATA_POOL['video_details'])
                # if any(df := pd.DataFrame(data,columns=data.keys(),index=[0])):
                #     st.write()
                #     st.write("-"*50)
                #     st.table(df)
                # else:
                #     st.write()
                #     st.write("-"*50)
                #     st.warning("no video details found")
        # st.write(main.DATA_POOL)

            main.get_every_video_in_playlist(temp_map[selected_playlist])

elif len(channel_list) > 1:
    
    channel_details_dict = {}
    playlist_details_dict = {}
    for channel in channel_list:
        channel_id = main.get_channel_id_by_handle(channel) if (channel[0] == '@') else main.get_channel_id_by_username(channel)
        if get_channel_info(channel_id):
            ch_det = main.DATA_POOL["channel_details"]
            pl_det = main.DATA_POOL["playlist_details"]
            channel_details_dict[channel] = ch_det
            playlist_details_dict[channel] = pl_det
    ch_det_df = pd.DataFrame(channel_details_dict[list(channel_list)[0]])
    pl_det_df = pd.DataFrame(playlist_details_dict[list(channel_list)[0]])

    for ch_no in range(1,len(channel_list)):
        df2 = pd.DataFrame(channel_details_dict[list(channel_list)[ch_no]])
        df4 = pd.DataFrame(playlist_details_dict[list(channel_list)[ch_no]])

        ch_det_df = ch_det_df.merge(df2,on=list(ch_det_df.columns),how="outer")
        pl_det_df = pl_det_df.merge(df4,on=list(pl_det_df.columns),how="outer")

    else:
        ch_det_df.drop("channel_description",axis=1)
        st.table(ch_det_df)
        st.table(pl_det_df)
    
else:
    pass


x = np.random.randint(20,100,20).reshape(20,1)
y = np.random.randint(20,100,20).reshape(20,1)

# dt = pd.DataFrame(np.hstack([x,y]),columns=("row","col"),)
# dt = pd.DataFrame({'row':[0,255],'col':[30,200]})
# st.table(dt)
# st.bar_chart(dt,x='row',y='col')

# import plotly.figure_factory as ff
# ff.create_
# st.plotly_chart()

if len(channel_list)>1:
    import plotly.figure_factory as ff
    details = {"ch_name":[],"view_count":[],"sub_count":[],"vid_count":[]}
    st.divider()
    div1,div2,div3 = st.columns([0.3,0.3,0.3])
    for channel in channel_list:
        if get_channel_info(main.get_channel_id_by_username(channel)):
            ch_grh = main.DATA_POOL["channel_details"]
            details["ch_name"].append(ch_grh["channel_name"][0])
            details["view_count"].append(int(ch_grh["channel_views"][0]))
            details["sub_count"].append(int(ch_grh["channel_subscriberCount"][0]))
            details["vid_count"].append(int(ch_grh["channel_videos"][0]))

    dat = pd.DataFrame(details)
    # st.table(dat)
    # st.write(dat)
    div1.bar_chart(dat,x="ch_name",y="sub_count",x_label="channels",y_label="subscribers")
    div2.bar_chart(dat,x="ch_name",y="vid_count",x_label="channels",y_label="videos")
    div3.bar_chart(dat,x="ch_name",y="view_count",x_label="channels",y_label="views")

    st.divider()
    st.line_chart(dat,x="ch_name",y="sub_count",)
    # fig = ff.create_distplot([dat["vid_count"],dat["view_count"],dat["sub_count"]],group_labels=dat["ch_name"],bin_size=10)
    fig = ff.create_2d_density(x=dat["view_count"],y=dat["sub_count"],title="Relation between views and subs")
    fig1 = ff.create_2d_density(x=dat["view_count"],y=dat["vid_count"],title="Relation between views and videos")
    fig2 = ff.create_2d_density(x=dat["sub_count"],y=dat["vid_count"],title="Relation between subs and videos")
    st.plotly_chart(fig)
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
elif len(channel_list)<=1 and len(channel_list)!=0:
    
    details = {"ch_name":[],"view_count":[],"sub_count":[],"vid_count":[]}
    st.divider()
    div1,div2,div3 = st.columns([0.3,0.3,0.3])
    for channel in channel_list:
        if get_channel_info(main.get_channel_id_by_username(channel)):
            ch_grh = main.DATA_POOL["channel_details"]
            
            details["ch_name"].append(ch_grh["channel_name"][0])
            details["view_count"].append(int(ch_grh["channel_views"][0]))
            details["sub_count"].append(int(ch_grh["channel_subscriberCount"][0]))
            details["vid_count"].append(int(ch_grh["channel_videos"][0]))

    dat = pd.DataFrame(details)
    # st.table(dat)
    # st.write(dat)
    div1.bar_chart(dat,x="ch_name",y="sub_count",x_label="channel",y_label="subscribers")
    div2.bar_chart(dat,x="ch_name",y="vid_count",x_label="channel",y_label="videos")
    div3.bar_chart(dat,x="ch_name",y="view_count",x_label="channel",y_label="views")
    # video_data = pd.DataFrame(sc_data)
    # for pl_item in main.DATA_POOL["playlist_items"]["item_id"]:
    #     temp_sc = pd.DataFrame(main.get_video_details(pl_item))
    #     st.table(temp_sc)
    #     video_data.merge(temp_sc,on="video_id",how="outer")
    # st.table(video_data)

_,u1,_ = st.columns([0.3,0.3,0.3])
if len(channel_list)>=1:
    if u1.button("upload to database",use_container_width=True):
        from database import db_run
        if db_run():
            st.balloons()








#TODO: add additional functionality to the get_video_details() so it gets the details of all the videos not only one

#TODO: for single channel display likes,view count,dislikes.
#TODO: also conncet to the database
# if there is single channel the value has to be a string instead of stroing it in a list