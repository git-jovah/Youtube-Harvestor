from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, create_engine
import pandas as pd

Base = declarative_base()

class Channel(Base):
    __tablename__ = "channel"
    channel_id = Column(String, primary_key=True)
    channel_name = Column(String)
    channel_views = Column(String)
    channel_description = Column(String)
    channel_videos = Column(String)
    channel_subscriberCount = Column(String)
    channel_status = Column(String)

class Playlist(Base):
    __tablename__ = "playlists"
    playlist_id = Column(String, primary_key=True)
    playlist_name = Column(String)
    playlist_date = Column(String)

class PlaylistItems(Base):
    __tablename__ = "playlist_items"
    item_id = Column(String, primary_key=True)
    item_name = Column(String)
    item_date = Column(String)
    item_status = Column(String)

class VideoData(Base):
    __tablename__ = "video_data"
    video_id = Column(String, primary_key=True)
    video_name = Column(String)
    video_date = Column(String)
    video_description = Column(String)
    video_views = Column(String)
    video_likes = Column(String)
    video_duration = Column(String)
    video_comments_count = Column(String)
    video_commentText = Column(String)
    video_caption_status = Column(String)
    video_thumbnail = Column(String)

engine = create_engine("sqlite:///tests/youtube_harv.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def clear_all_tables():
    session = Session()
    session.query(Channel).delete()
    session.query(Playlist).delete()
    session.query(PlaylistItems).delete()
    session.query(VideoData).delete()
    session.commit()
    session.close()

def db_run(channels_df: pd.DataFrame, playlists_df: pd.DataFrame = None, videos_df: pd.DataFrame = None) -> bool:
    """
    Upload channels, playlists, and videos to database.
    """
    try:
        session = Session()
        clear_all_tables()

        if not channels_df.empty:
            for _, row in channels_df.iterrows():
                ch = Channel(
                    channel_id=row["channel_id"],
                    channel_name=row["channel_name"],
                    channel_views=str(row["channel_views"]),
                    channel_description=row["channel_description"],
                    channel_videos=str(row["channel_videos"]),
                    channel_subscriberCount=str(row["channel_subscriberCount"]),
                    channel_status=row.get("channel_status", "")
                )
                session.add(ch)

        if playlists_df is not None and not playlists_df.empty:
            for _, row in playlists_df.iterrows():
                pl = Playlist(
                    playlist_id=row["playlist_id"],
                    playlist_name=row["playlist_name"],
                    playlist_date=row.get("playlist_date", "")
                )
                session.add(pl)

        if videos_df is not None and not videos_df.empty:
            for _, row in videos_df.iterrows():
                vid = PlaylistItems(
                    item_id=row["video_id"],
                    item_name=row["video_title"],
                    item_date=row.get("video_date", ""),
                    item_status=row.get("video_status", "")
                )
                session.add(vid)

        session.commit()
        session.close()
        return True
    except Exception as e:
        print("Database upload failed:", e)
        return False
