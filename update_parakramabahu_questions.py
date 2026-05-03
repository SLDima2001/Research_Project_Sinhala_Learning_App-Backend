import json
import codecs

with codecs.open('data/stories.json', 'r', 'utf-8') as f:
    stories = json.load(f)

for story in stories:
    if story['id'] == 'story_parakramabahu':
        story['segments']['branch_a']['question_timestamps'] = [10000, 20000, 30000]
        story['segments']['branch_a']['question_pool'] = [
          {
            "id": "qA1",
            "text": "රජතුමා ගත් තීරණය කුමක්ද?",
            "options": ["ගැටලුව නොසලකා හැරීම", "වැව් ඉදි කිරීම"],
            "correct_index": 1
          },
          {
            "id": "qA2",
            "text": "ගොවීන්ට ජලය ලැබුණේ ඇයි?",
            "options": ["වැව් නිසා", "වැසි නැති නිසා"],
            "correct_index": 0
          },
          {
            "id": "qA3",
            "text": "රටේ තත්වය කෙසේ වෙනස් වුණාද?",
            "options": ["සම්පන්න වුණා", "නරක වුණා"],
            "correct_index": 0
          },
          {
            "id": "qA4",
            "text": "රජතුමා ගැටලුවට කුමක් කළාද?",
            "options": ["විසඳුමක් සෙව්වා", "පලා ගියා"],
            "correct_index": 0
          },
          {
            "id": "qA5",
            "text": "ජලය වැදගත් වන්නේ ඇයි?",
            "options": ["වගා සඳහා අවශ්‍ය නිසා", "විහිළු සඳහා"],
            "correct_index": 0
          },
          {
            "id": "qA6",
            "text": "මෙම කතාවෙන් ලැබෙන පාඩම කුමක්ද?",
            "options": ["සම්පත් හොඳින් භාවිතා කිරීම", "නොසලකා හැරීම"],
            "correct_index": 0
          }
        ]

        story['segments']['branch_b']['question_timestamps'] = [10000, 20000, 30000]
        story['segments']['branch_b']['question_pool'] = [
          {
            "id": "qB1",
            "text": "රජතුමා කළේ කුමක්ද?",
            "options": ["නොසලකා හැරියා", "වැව් ඉදි කළා"],
            "correct_index": 0
          },
          {
            "id": "qB2",
            "text": "ගොවීන්ට ජලය ලැබුණාද?",
            "options": ["ඔව්", "නැහැ"],
            "correct_index": 1
          },
          {
            "id": "qB3",
            "text": "වගා වලට සිදු වූ දේ කුමක්ද?",
            "options": ["නසුණා", "වැඩි වුණා"],
            "correct_index": 0
          },
          {
            "id": "qB4",
            "text": "රටේ තත්වය කුමක්ද?",
            "options": ["නරක වුණා", "හොඳ වුණා"],
            "correct_index": 0
          },
          {
            "id": "qB5",
            "text": "රජතුමාගේ තීරණය හොඳද?",
            "options": ["නැහැ", "ඔව්"],
            "correct_index": 0
          },
          {
            "id": "qB6",
            "text": "මෙම කතාවෙන් ලැබෙන පාඩම කුමක්ද?",
            "options": ["ගැටලු විසඳීම වැදගත් බව", "නොසලකා හැරීම"],
            "correct_index": 0
          }
        ]
        break

with codecs.open('data/stories.json', 'w', 'utf-8') as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)

print('Successfully updated Parakramabahu questions')
