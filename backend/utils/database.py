from pymongo import MongoClient
from dotenv import load_dotenv
import os


class Database:
    def __init__(self, db_name):
        self.client = MongoClient(os.environ['CONNECTION_STRING'])
        self.db = self.client[db_name]
        self.chats = self.db['chats']
        self.endpoints = self.db["endpoints"]

    def get_sessions_by_user_id(self, user_id, limit=10):
        # Get the existing document
        doc = self.chats.find_one()

        # Filter the sessions by user ID
        sessions = doc.get('sessions', [])
        user_sessions = [session for session in sessions if session['session'][0]['user'] == user_id]

        # Return only the last 'limit' sessions
        return user_sessions[-limit:]
    
    def insert_call_chats(self, messages):
        self.chats.insert_one(messages)


    def get_all_proposals(self):
        proposal_collection = self.db['proposal']
        proposals = proposal_collection.find()
        return list(proposals)
    
    def get_texts_by_user_id(self, user_id):
        doc = self.chats.find_one()
        sessions = doc.get('sessions', [])
        user_sessions = [session for session in sessions if session['user'] == user_id]
        user_texts = [session['message'] for session in user_sessions]

        return user_texts
    
    def save_proposal(self, proposal_data):
        proposal_collection = self.db['proposal']
        proposal_collection.delete_many({})
        proposal_collection.insert_one(proposal_data)

    def append_session(self, session):
        # If there's no document, create one with an empty list
        if self.chats.count_documents({}) == 0:
            self.chats.insert_one({'sessions': []})

        # Get the existing document
        doc = self.chats.find_one()

        # Append the new session to the list of sessions
        sessions = doc.get('sessions', [])
        sessions.append(session)

        # Update the document
        self.chats.update_one({}, {'$set': {'sessions': sessions}})

    

    async def update_endpoint(self, endpoint):
        filter_query = {"endpoint": endpoint}
        update_operation = {"$inc": {"count": 1}}
        self.endpoints.update_one(filter_query, update_operation, upsert=True)

