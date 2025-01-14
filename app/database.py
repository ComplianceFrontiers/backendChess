from pymongo import MongoClient
from gridfs import GridFS
import os

client = None
db = None
fs = None
admin_collection = None
users_collection = None
schoolform_coll=None
demo_user=None
app_signup=None
bulkemail=None
email_request=None
form_chess_club=None
form_Wilmington_Chess_Coaching=None
form_Bear_Middletown_Chess_Tournament=None

def init_db(app):
    global client, db, fs, admin_collection, users_collection,schoolform_coll,demo_user,app_signup,bulkemail,email_request,form_chess_club,form_Wilmington_Chess_Coaching,form_Bear_Middletown_Chess_Tournament
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client.chessDb
    db1=client.demo
    admin_collection = db.admin_db
    users_collection = db.users
    schoolformdb=client.chessschool
    schoolform_coll=schoolformdb.kids 
    demo_user=db1.demo_user
    app_signup=schoolformdb.app_signup
    bulkemail=schoolformdb.bulkemail
    email_request=schoolformdb.email_request
    form_chess_club=schoolformdb.form_chess_club
    form_Wilmington_Chess_Coaching=schoolformdb.form_Wilmington_Chess_Coaching
    form_Bear_Middletown_Chess_Tournament=schoolformdb.form_Bear_Middletown_Chess_Tournament
    fs = GridFS(db)
