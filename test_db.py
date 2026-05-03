import os
import asyncio
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = "sinhala_learning_app"

async def test_conn():
    print(f"Testing connection to {MONGODB_URL}")
    client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=certifi.where())
    try:
        # The ismaster command is cheap and does not require auth.
        # But we want to test auth, so we should try to list collections or something.
        await client[DB_NAME].command("ping")
        print("Ping successful!")
        cols = await client[DB_NAME].list_collection_names()
        print(f"Collections: {cols}")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_conn())
