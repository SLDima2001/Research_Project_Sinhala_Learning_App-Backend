import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://root:Dima2001@customerfeedback.83hfgpu.mongodb.net/?retryWrites=true&w=majority&appName=customerfeedback")

client = MongoClient(MONGO_URI)
for db_name in ['customerfeedback', 'sinhala_learning_app']:
    db = client[db_name]
    count = db['users'].count_documents({})
    print(f"{db_name}.users count: {count}")
    if count > 0:
        print(f"Sample user from {db_name}: {db['users'].find_one({}, {'password': 0})}")
