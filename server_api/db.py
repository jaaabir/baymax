from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json 


class MonDb:
    def __init__(self, uri, db_name, collection_name):
        self.db  = self.connect_db(uri, db_name)
        self.col = collection_name 
    
    def connect_db(self, uri, name):
        client = MongoClient(uri)
        return client[name]
    
    def user_in_db(self, id, return_type = 'obj'):
        history = self.db[self.col].find_one({
            'id' : ObjectId(id)
            })
        
        if return_type == 'bool':
            return history != None
        
        return history
    
    def upload_history(self, history):
        self.db[self.col].insert_one(history)
        
class LocDb:
    def __init__(self, filename = 'local_history.json'):
        self.filename = filename
        self.create_db()
        
    def create_db(self):
        if self.filename not in os.listdir():
            data = {'userId' : ['symptoms']}
            with open(self.filename, 'w') as file:
                json.dump(data, file)
                
    def load_db(self):
        data = None
        with open(self.filename, 'r') as file:
            data = json.load(file)
        return data 
    
    def save_db(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent = 6)
    
    def add_user_symp(self, userId, data):
        jdb = self.load_db()
        if userId in jdb.keys():
            jdb[userId] += data
        else:
            jdb[userId] = data
            
        self.save_db(jdb)
    
    def del_user(self, userId):
        jdb = self.load_db()
        jdb = {k : v for k,v in jdb.items() if k != userId}  
        self.save_db(jdb)
        
        
        
    
            
            
        
        
