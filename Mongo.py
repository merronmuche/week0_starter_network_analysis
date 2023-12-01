from pymongo import MongoClient

from mongoengine import (Document, StringField, IntField, BooleanField, 
                         EmbeddedDocument, EmbeddedDocumentField, 
                         EmbeddedDocumentListField, ListField, connect)


client = MongoClient('mongodb://localhost:27017/')
db = client['slack_massage']
collection = db['slack']


# Connect to MongoDB
connect('slack_massage', host='localhost', port=27017)

class UserProfile(EmbeddedDocument):
    avatar_hash = StringField()
    image_72 = StringField()
    first_name = StringField()
    real_name = StringField()
    display_name = StringField()
    team = StringField()
    name = StringField()
    is_restricted = BooleanField()
    is_ultra_restricted = BooleanField()


class Reaction(EmbeddedDocument):
    name = StringField()
    users = ListField(StringField())
    count = IntField()

class Message(Document):
    client_msg_id = StringField()
    type = StringField(required=True)
    text = StringField()
    user = StringField(required=True)
    ts = StringField(required=True)
    blocks = ListField()  # Further definition depends on the structure of blocks
    team = StringField()
    user_team = StringField()
    source_team = StringField()
    user_profile = EmbeddedDocumentField(UserProfile)
    reactions = EmbeddedDocumentListField(Reaction)
    # Additional fields for 'subtype', 'inviter' based on your data
    subtype = StringField()
    inviter = StringField()

# Inserting a document into the collection
document = {"name": "John Doe", "email": "john@example.com"}
collection.insert_one(document)