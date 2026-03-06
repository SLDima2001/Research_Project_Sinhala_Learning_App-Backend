import json
import os
from flask import Blueprint, request, jsonify
from pathlib import Path

stories_bp = Blueprint('stories', __name__)

# Config
DATA_PATH = Path(__file__).parent / "data" / "stories.json"

def get_stories_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@stories_bp.route('/stories', methods=['GET'])
def get_stories():
    stories = get_stories_data()
    return jsonify([{"id": s.get('id'), "title": s.get('title')} for s in stories])

@stories_bp.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    stories = get_stories_data()
    for s in stories:
        if s.get('id') == story_id:
            return jsonify(s)
    return jsonify({"error": "Story not found"}), 404

@stories_bp.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json()
    answers = data.get("answers", {})
    score = len(answers) * 10
    return jsonify({"score": score, "feedback": "Good job! You completed the quiz."})
