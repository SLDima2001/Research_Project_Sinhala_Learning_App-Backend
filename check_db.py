import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback")

client = MongoClient(MONGO_URI)
try:
    print("Databases:")
    for db_name in client.list_database_names():
        db = client[db_name]
        print(f" - {db_name} (Collections: {db.list_collection_names()})")
except Exception as e:
    print(f"Error: {e}")
