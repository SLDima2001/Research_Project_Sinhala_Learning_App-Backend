import json
from pathlib import Path
from typing import List, Dict, Optional
from ..models.schemas import Story

DATA_PATH = Path(__file__).parent.parent / "data" / "stories.json"

class StoryService:
    def __init__(self):
        self.stories: Dict[str, Story] = {}
        self.load_data()

    def load_data(self):
        if not DATA_PATH.exists():
            return
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                story = Story(**item)
                self.stories[story.id] = story

    def get_all_stories(self):
        self.load_data() # Force reload for dev
        return [{"id": s.id, "title": s.title} for s in self.stories.values()]

    def get_story(self, story_id: str) -> Optional[Story]:
        self.load_data() # Force reload for dev
        return self.stories.get(story_id)

    def get_scene(self, story_id: str, scene_id: str):
        story = self.stories.get(story_id)
        if not story:
            return None
        
        # Check Legacy Scenes
        if story.scenes and scene_id in story.scenes:
            return story.scenes[scene_id]

        # Check Video Interactions (New Format)
        if story.interactions and scene_id in story.interactions:
            # Convert interaction to a generic scene-like object for the frontend if needed
            # OR just return it as is, depending on pydantic model. Validating against 'Scene' model might fail if fields differ.
            # But the frontend seems to request "interactions" via next_segment_id, so the API might not even be hit for interactions *if* the frontend has the full story object.
            # Wait, StoryScreen.js loads the FULL story (getStory), not individual scenes (get_scene).
            # The get_scene API might be used by "NarrativeScene" or other legacy components.
            # Let's see if we need to support it. 
            # If the frontend downloads the whole story at once (which it does in StoryScreen.js:43), then get_scene is only used if something explicitly calls it.
            # But let's support it for robustness.
            return story.interactions[scene_id]
            
        return None

service = StoryService()
