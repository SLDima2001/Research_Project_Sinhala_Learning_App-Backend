from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class Choice(BaseModel):
    text: str
    next_scene_id: Optional[str] = None

class Vocabulary(BaseModel):
    word: str
    meaning: str
    pronunciation: str

class Scene(BaseModel):
    type: Optional[str] = "narrative" # narrative, decision, activity, quiz, end
    text: Optional[str] = None
    image: Optional[str] = None
    audio: Optional[str] = None
    video: Optional[bool] = None
    vocabulary: Optional[List[Vocabulary]] = []
    choices: Optional[List[Choice]] = []
    # Activity specific
    activity_type: Optional[str] = None
    target_word: Optional[str] = None
    options: Optional[List[Dict]] = [] # For activity/quiz options
    # Quiz specific
    questions: Optional[List[Dict]] = []
    next_scene_id: Optional[str] = None

class Segment(BaseModel):
    video_id: Optional[str] = None
    start_time: int
    end_time: int
    next_segment_id: str

class InteractionOption(BaseModel):
    text: str
    next_segment_id: Optional[str] = None
    is_correct: Optional[bool] = None

class Interaction(BaseModel):
    type: str # decision, quiz
    text: str
    options: List[InteractionOption]
    next_segment_id: Optional[str] = None

class Story(BaseModel):
    id: str
    title: str
    type: Optional[str] = "legacy" # legacy, video_interactive
    # Legacy
    scenes: Optional[Dict[str, Scene]] = None
    # Video Interactive
    default_video: Optional[str] = None
    segments: Optional[Dict[str, Segment]] = None
    interactions: Optional[Dict[str, Interaction]] = None

class StoryListResponse(BaseModel):
    id: str
    title: str
