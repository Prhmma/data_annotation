import pymongo
import random

class MongoDB:
    def __init__(self, connection_string, db_name, collection_name):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_random_document(self):
        count = self.collection.count_documents({})
        random_index = random.randint(0, count - 1)
        return self.collection.find().limit(1).skip(random_index).next()

    def append_to_history(self, document_id, new_history_item):
        doc = self.collection.find_one({"_id": document_id})
        
        if "history" not in doc or not isinstance(doc["history"], list):
            update_operation = {"$set": {"history": [new_history_item]}}
        else:
            update_operation = {"$push": {"history": new_history_item}}
        
        self.collection.update_one({"_id": document_id}, update_operation)

    def get_history(self, document_id):
        doc = self.collection.find_one({"_id": document_id})
        if "history" in doc and isinstance(doc["history"], list):
            return doc["history"]
        return []

    def close_connection(self):
        self.client.close()