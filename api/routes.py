from fastapi import APIRouter, HTTPException
from services.engine import service
from models.schemas import Story, Scene, StoryListResponse

router = APIRouter()

@router.get("/stories", response_model=list[StoryListResponse])
async def get_stories():
    return await service.get_all_stories()

@router.get("/stories/{story_id}", response_model=Story)
async def get_story_full(story_id: str):
    story = await service.get_story(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.get("/stories/{story_id}/scenes/{scene_id}", response_model=Scene)
async def get_scene(story_id: str, scene_id: str):
    scene = await service.get_scene(story_id, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.post("/quiz/submit")
def submit_quiz(data: dict):
    # Simple scoring logic: 10 points per answer
    answers = data.get("answers", {})
    score = len(answers) * 10 
    
    # In a real app, you would validate against correct answers here.
    # For now, we assume any answer is worth points for demonstration.
    
    return {"score": score, "feedback": "Good job! You completed the quiz."}
