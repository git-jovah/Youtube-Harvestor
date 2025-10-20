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

# create a database engine
engine = create_engine('sqlite:///test_db.db')

# create the table in database
base.metadata.create_all(engine)

# 5. Create a session to interact with the DB
Session = sessionmaker(bind=engine)
session = Session()

# 6. Add some users
user1 = User(name='Alice', age=30)
user2 = User(name='Bob', age=25)

session.add(user1)
session.add(user2)
session.commit()

# 7. Query the database
users = session.query(User).all()
for user in users:
    print(user)

# 8. Close the session
session.close()