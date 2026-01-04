from fastapi import APIRouter, HTTPException
from typing import Union
from ..services.engine import service
from ..models.schemas import Story, Scene, StoryListResponse

router = APIRouter()

@router.get("/stories", response_model=list[StoryListResponse])
def get_stories():
    return service.get_all_stories()

@router.get("/stories/{story_id}", response_model=Story)
def get_story_full(story_id: str):
    story = service.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.get("/stories/{story_id}/scenes/{scene_id}", response_model=Union[Scene, dict])
def get_scene(story_id: str, scene_id: str):
    scene = service.get_scene(story_id, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.post("/quiz/submit")
def submit_quiz(data: dict):
    # Placeholder for quiz logic
    return {"score": 10, "feedback": "Good job!"}
