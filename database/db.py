from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import Column,Integer,String,create_engine
import sqlite3

# Database = sqlite3.connect("test.sqlite")
# cursor = Database.cursor()

# cursor.execute('''
#     CREATE TABLE IF NOT EXIST tests(
#     id INTEGERS PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     age INTEGER)

# ''')
# base class for the model
base = declarative_base()


# creating the table
class User(base):
    __tablename__ = "user"
    
    id = Column(Integer,primary_key=True)
    name = Column(String)
    age = Column(Integer)

    def __repr__(self):
        return f"User(id={self.id},name={self.name},age={self.age})"
    
class Channel(base):
    __tablename__="channel"

    channel_id              = Column(String,primary_key=True)
    channel_name            = Column(String)
    channel_views           = Column(String)
    channel_description     = Column(String)
    channel_videos          = Column(String)
    channel_subscriberCount = Column(String)
    channel_status          = Column(String)

class playlist(base):
    __tablename__ = "playlists"

    playlist_name = Column(String)
    playlist_id   = Column(String,primary_key=True)
    playlist_date = Column(String)

class playlist_items(base):
    __tablename__ = "PlaylistItems"

    item_name   = Column(String)
    item_id     = Column(String,primary_key=True)
    item_date   = Column(String)
    item_status = Column(String)

class VideoData(base):
    __tablename__ = "VideoData"

    video_name           = Column(String)
    video_id             = Column(String,primary_key=True)
    video_date           = Column(String)
    video_description    = Column(String)
    video_views          = Column(String)
    video_likes          = Column(String)
    video_duration       = Column(String)
    video_comments_count = Column(String)
    video_commentText    = Column(String)
    video_caption_status = Column(String)
    video_thumbnail      = Column(String)

# create a database engine
engine = create_engine('sqlite:///tests/tests.db')

# create the table in database
base.metadata.create_all(engine)

# 5. Create a session to interact with the DB
Session = sessionmaker(bind=engine)
session = Session()

# 6. Add some users
def db_run():
    import main
    __data__ = main.DATA_POOL["channel_details"]
    ch1 = Channel(  channel_id = __data__['channel_id'][0],
                    channel_name = __data__['channel_name'][0],
                    channel_views = __data__['channel_views'][0],
                    channel_description = __data__['channel_description'][0],
                    channel_videos = __data__['channel_videos'][0],
                    channel_subscriberCount = __data__['channel_subscriberCount'][0],
                    channel_status = __data__['channel_status'][0]
    )
    session.add(ch1)
    session.commit()

    # 7. Query the database
    users = session.query(User).all()
    for user in users:
        print(user)

    # 8. Close the session
    session.close()
    return True