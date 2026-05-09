import json
from pathlib import Path
from typing import List, Dict, Optional
from ..models import schemas
from ..database import db

DATA_PATH = Path(__file__).parent.parent / "data" / "stories.json"

class StoryService:
    def __init__(self):
        pass

    async def get_collection(self, name):
        return db.get_db()[name]

    async def seed_data(self):
        """Load data from JSON to MongoDB if collection is empty"""
        try:
            collection = await self.get_collection("stories")
            count = await collection.count_documents({})
            
            
            
            

            if not DATA_PATH.exists():
                return

            print("Seeding database from stories.json...")
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    from pymongo import UpdateOne
                    operations = []
                    for item in data:
                        
                        try:
                            
                            story_obj = schemas.Story(**item)
                            
                            
                            item_dict = story_obj.dict()
                            item_dict['_id'] = item_dict['id']
                            
                            
                            operations.append(
                                UpdateOne({"_id": item_dict['_id']}, {"$set": item_dict}, upsert=True)
                            )
                        except Exception as validation_err:
                            print(f"Skipping invalid story {item.get('id')}: {validation_err}")
                    
                    if operations:
                        await collection.bulk_write(operations)
                        print(f"Seeded/Updated {len(operations)} stories with schema validation.")

        except Exception as e:
            print(f"Error seeding database: {e}")

    async def get_all_stories(self) -> List[schemas.StoryListResponse]:
        collection = await self.get_collection("stories")
        stories_cursor = collection.find({})
        results = []
        async for s in stories_cursor:
            results.append(schemas.StoryListResponse(id=s['id'], title=s['title']))
        return results

    async def get_story(self, story_id: str) -> Optional[schemas.Story]:
        collection = await self.get_collection("stories")
        story_data = await collection.find_one({"id": story_id})
        
        if not story_data:
            return None
        
        
        
        return schemas.Story(**story_data)

    async def get_scene(self, story_id: str, scene_id: str):
        story = await self.get_story(story_id)
        if story and story.scenes and scene_id in story.scenes:
            return story.scenes[scene_id]
        return None

service = StoryService()
