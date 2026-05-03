import json
import codecs

with codecs.open('data/stories.json', 'r', 'utf-8') as f:
    stories = json.load(f)

new_story = {
    'id': 'story_parakramabahu',
    'title': 'මහා පරාක්‍රමබාහු රජතුමා (King Parakramabahu)',
    'type': 'video_interactive',
    'category': 'hard',
    'segments': {
      'main_segment': {
        'video_id': 'parakramabahu_main',
        'start_time': 0,
        'end_time': 600000,
        'next_segment_id': 'decision_1',
        'question_timestamps': [],
        'question_pool': []
      },
      'branch_a': {
        'video_id': 'parakramabahu_a',
        'start_time': 0,
        'end_time': 600000,
        'next_segment_id': 'end_screen',
        'question_timestamps': [10000, 20000, 30000],
        'question_pool': [
          {
            'id': 'qA1',
            'text': 'රජතුමා ගත් තීරණය කුමක්ද?',
            'options': ['ගැටලුව නොසලකා හැරීම', 'වැව් ඉදි කිරීම'],
            'correct_index': 1,
            'timestamp': 10000
          },
          {
            'id': 'qA2',
            'text': 'වැව් ඉදි කිරීමෙන් ලැබුණු ප්‍රයෝජනය කුමක්ද?',
            'options': ['ජලය ලැබුණා', 'වගා නසුණා'],
            'correct_index': 0,
            'timestamp': 20000
          },
          {
            'id': 'qA3',
            'text': 'රටේ තත්වය කෙසේ වෙනස් වුණාද?',
            'options': ['සම්පන්න වුණා', 'නරක වුණා'],
            'correct_index': 0,
            'timestamp': 30000
          }
        ]
      },
      'branch_b': {
        'video_id': 'parakramabahu_b',
        'start_time': 0,
        'end_time': 600000,
        'next_segment_id': 'end_screen',
        'question_timestamps': [10000, 20000, 30000],
        'question_pool': [
          {
            'id': 'qB1',
            'text': 'රජතුමා කළේ කුමක්ද?',
            'options': ['විසඳුමක් සොයාගත්තා', 'නොසලකා හැරියා'],
            'correct_index': 1,
            'timestamp': 10000
          },
          {
            'id': 'qB2',
            'text': 'ගොවීන්ට ජලය ලැබුණාද?',
            'options': ['ඔව්', 'නැහැ'],
            'correct_index': 1,
            'timestamp': 20000
          },
          {
            'id': 'qB3',
            'text': 'එයින් ඇති වූ ප්‍රතිඵලය කුමක්ද?',
            'options': ['නරක ප්‍රතිඵලයක්', 'හොඳ ප්‍රතිඵලයක්'],
            'correct_index': 0,
            'timestamp': 30000
          }
        ]
      }
    },
    'interactions': {
      'decision_1': {
        'type': 'decision',
        'text': 'රජතුමා කුමක් කරන්නේද?',
        'options': [
          {
            'text': 'A) වැව් ඉදි කිරීම',
            'next_segment_id': 'branch_a'
          },
          {
            'text': 'B) ගැටලුව නොසලකා හැරීම',
            'next_segment_id': 'branch_b'
          }
        ]
      }
    }
}

# Add if not exists
existing = next((s for s in stories if s['id'] == 'story_parakramabahu'), None)
if not existing:
    stories.append(new_story)
else:
    stories[stories.index(existing)] = new_story

with codecs.open('data/stories.json', 'w', 'utf-8') as f:
    json.dump(stories, f, ensure_ascii=False, indent=2)

print('Successfully added to JSON')
