import os
import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# Default to local MongoDB, but allow override via env var
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    MONGODB_URL = "mongodb://localhost:27017"
    
DB_NAME = "sinhala_learning_app"

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        self.client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=certifi.where())
        self.db = self.client[DB_NAME]
        print(f"Connected to MongoDB at {MONGODB_URL}")

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def get_db(self):
        return self.db

db = Database()
