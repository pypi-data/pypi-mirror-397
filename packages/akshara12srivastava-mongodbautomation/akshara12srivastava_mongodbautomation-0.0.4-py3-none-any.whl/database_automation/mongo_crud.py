from typing import Any
import os
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json


class mongo_operation:
    __collection = None  # Private/protected variable
    __database = None
    
    def __init__(self, client_url: str, database_name: str, collection_name: str = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name
       
    def create_mongo_client(self, collection=None):
        # Fixed: Add SSL/TLS support for MongoDB Atlas
        client = MongoClient(
            self.client_url,
            server_api=ServerApi('1'),
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        return client
    
    def create_database(self, collection=None):
        if mongo_operation.__database == None:
            client = self.create_mongo_client(collection)
            mongo_operation.__database = client[self.database_name]
        return mongo_operation.__database
    
    def create_collection(self, collection_name=None):
        # Use provided collection_name or fall back to instance variable
        if collection_name:
            target_collection = collection_name
        else:
            target_collection = self.collection_name
            
        if mongo_operation.__collection == None or mongo_operation.__collection != target_collection:
            database = self.create_database()
            self.collection = database[target_collection]
            mongo_operation.__collection = target_collection
            
        return self.collection
    
    def insert_record(self, record: dict, collection_name: str) -> Any:
        if type(record) == list:
            for data in record:
                if type(data) != dict:
                    raise TypeError("record must be in the dict")    
            collection = self.create_collection(collection_name)
            collection.insert_many(record)
        elif type(record) == dict:
            collection = self.create_collection(collection_name)
            collection.insert_one(record)
        
        print("Record(s) inserted successfully!")
        return True
    
    def bulk_insert(self, datafile, collection_name: str = None):
        self.path = datafile
        
        if self.path.endswith('.csv'):
            dataframe = pd.read_csv(self.path, encoding='utf-8')
            
        elif self.path.endswith(".xlsx"):
            dataframe = pd.read_excel(self.path)
        else:
            raise ValueError("File must be .csv or .xlsx")
            
        datajson = json.loads(dataframe.to_json(orient='records'))
        
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)
        
        print(f"Bulk insert completed: {len(datajson)} records inserted!")
        return True