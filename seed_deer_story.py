import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "sinhala_learning_app"

async def seed_deer_story():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    collection = db["stories"]
    
    deer_story = {
        "_id": "story_deer",
        "id": "story_deer",
        "title": "රන්වන් මුවා (The Golden Deer)",
        "type": "video_interactive",
        "segments": {
            "intro": {
                "video_id": "deer_intro.mp4",
                "start_time": 0,
                "end_time": 30000, # Assume intro is 30s for now
                "next_segment_id": "choice_popup",
                "question_timestamps": [],
                "question_pool": []
            },
            "branch_a": {
                "video_id": "deer_A.mp4",
                "start_time": 0,
                "end_time": 300000, # Assume 5 mins video
                "next_segment_id": "end_screen",
                "question_timestamps": [5000, 10000, 15000, 20000, 25000],
                "question_pool": [
                    {
                        "id": "qA1", "text": "රන්වන් මුවා ජීවත් වූයේ කොහේද?",
                        "options": ["නගරයක", "වනාන්තරයක", "පාරක", "කූඩුවක"], "correct_index": 1, "timestamp": 5000
                    },
                    {
                        "id": "qA2", "text": "වනාන්තරය මැදින් ඇවිදගෙන ගියේ කවුද?",
                        "options": ["රජතුමා", "සාමාන්ය මිනිසෙක්", "වඳුරෙක්", "සෙබළෙක්"], "correct_index": 1, "timestamp": 5000
                    },
                    {
                        "id": "qA3", "text": "හදිසියේම මිනිසා වැටුණේ කොතැනටද?",
                        "options": ["ගැඹුරු ගඟට", "ගසක් උඩට", "අඳුරු ගුහාවකට", "වැලි ගොඩකට"], "correct_index": 0, "timestamp": 5000
                    },
                    {
                        "id": "qA4", "text": "මිනිසා ගඟේ ගසාගෙන යන විට කෑගැසුවේ ඇයි?",
                        "options": ["සින්දු කියන්න", "උදව් ඉල්ලන්න", "තරහ ගිය නිසා", "සතුටට"], "correct_index": 1, "timestamp": 10000
                    },
                    {
                        "id": "qA5", "text": "රන්වන් මුවාට ඇසුණු ශබ්දය කුමක්ද?",
                        "options": ["කුරුල්ලන්ගේ සින්දු", "හුළඟ හමන හඬ", "මිනිසාගේ උදව් ඉල්ලීම", "වැසි ශබ්දය"], "correct_index": 2, "timestamp": 10000
                    },
                    {
                        "id": "qA6", "text": "මිනිසා බේරා ගැනීමට මුවා කළේ කුමක්ද?",
                        "options": ["පැන ගියා", "ගඟට පැන පිහිනා ගියා", "ගසක් පිටුපස සැඟවුණා", "නිදාගත්තා"], "correct_index": 1, "timestamp": 10000
                    },
                    {
                        "id": "qA7", "text": "මුවා විසින් මිනිසා ගෙන ගියේ කොතැනටද?",
                        "options": ["තමන්ගේ ගෙදරට", "ගඟේ ආරක්ෂිත ඉවුරට", "රජ මාලිගාවට", "කන්ද මුදුනට"], "correct_index": 1, "timestamp": 15000
                    },
                    {
                        "id": "qA8", "text": "මුවා තමන්ව බේරා ගත් විට මිනිසාට දැනුණේ කුමක්ද?",
                        "options": ["සතුටක් සහ කෘතඥතාවක්", "දැඩි කෝපයක්", "නිදිමතක්", "බයක්"], "correct_index": 0, "timestamp": 15000
                    },
                    {
                        "id": "qA9", "text": "මුවාගෙන් සමුගත් පසු මිනිසා ගියේ කොහේද?",
                        "options": ["වනාන්තරයට", "රජ මාලිගාවට", "ගඟ මැදට", "කන්දකට"], "correct_index": 1, "timestamp": 15000
                    },
                    {
                        "id": "qA10", "text": "මිනිසා රජතුමාට විස්තර කළේ කා ගැනද?",
                        "options": ["වලසෙක් ගැන", "රන්වන් මුවා ගැන", "කුරුල්ලෙක් ගැන", "අලියෙක් ගැන"], "correct_index": 1, "timestamp": 20000
                    },
                    {
                        "id": "qA11", "text": "මුවා ගැන ඇසූ විට රජතුමාට ඇති වූ හැඟීම කුමක්ද?",
                        "options": ["මුවා දැකීමට ආසාවක් ඇතිවීම", "නිදිමතක් ඇතිවීම", "කේන්තියක් ඇතිවීම", "දුකක්"], "correct_index": 0, "timestamp": 20000
                    },
                    {
                        "id": "qA12", "text": "රජතුමාට මුවා මුණගැසුණේ කොහේද?",
                        "options": ["මාලිගාවේදී", "නිදහස් වනාන්තරයේදී", "පාරේදී", "ගඟේදී"], "correct_index": 1, "timestamp": 20000
                    },
                    {
                        "id": "qA13", "text": "මුවා රජතුමාට කියා දුන් වැදගත් පාඩම කුමක්ද?",
                        "options": ["සටන් කරන හැටි", "කරුණාව සහ කළගුණ සැලකීම", "දඩයම් කරන හැටි", "දුවන හැටි"], "correct_index": 1, "timestamp": 25000
                    },
                    {
                        "id": "qA14", "text": "මුවාගේ වචන ඇසූ රජතුමාට තමන් ගැනම දැනුණේ කුමක්ද?",
                        "options": ["ලැජ්ජාවක් සහ පසුතැවීමක්", "ලොකු ආඩම්බරයක්", "තවත් කේන්තියක්", "සතුටක්"], "correct_index": 0, "timestamp": 25000
                    },
                    {
                        "id": "qA15", "text": "අවසානයේ රජතුමා ගත් තීරණය කුමක්ද?",
                        "options": ["මුවාව මැරීම", "මුවාව සහ වනාන්තරය ආරක්ෂා කිරීම", "මුවාව අල්ලා ගැනීම", "පැන යාම"], "correct_index": 1, "timestamp": 25000
                    }
                ]
            },
            "branch_b": {
                "video_id": "deer_B.mp4",
                "start_time": 0,
                "end_time": 300000,
                "next_segment_id": "end_screen",
                "question_timestamps": [7000, 14000, 20000, 25000, 30000],
                "question_pool": [
                    {
                        "id": "qB1", "text": "මුවා වනාන්තරයේ ඇවිදින විට දුටුවේ කවුද?",
                        "options": ["සෙල්ලම් කරන ළමයෙක්", "දුන්නක් අතින් ගත් දඩයක්කාරයෙක්", "අලියෙක්", "ගොවියෙක්"], "correct_index": 1, "timestamp": 7000
                    },
                    {
                        "id": "qB2", "text": "දඩයක්කාරයා වනාන්තරයට ආවේ ඇයි?",
                        "options": ["සතුන් දඩයම් කිරීමට", "මල් කැඩීමට", "නෑමට", "නිදා ගැනීමට"], "correct_index": 0, "timestamp": 7000
                    },
                    {
                        "id": "qB3", "text": "දඩයක්කාරයා මුවා දෙසට එල්ල කළේ කුමක්ද?",
                        "options": ["මල් මාලයක්", "තියුණු ඊතලයක්", "කැමරාවක්", "කෑමක්"], "correct_index": 1, "timestamp": 7000
                    },
                    {
                        "id": "qB4", "text": "හදිසියේම දඩයක්කාරයාට සිදු වූ අනතුර කුමක්ද?",
                        "options": ["වැස්සට තෙමීම", "පය ලිස්සා ගැඹුරු වලකට වැටීම", "නිදා වැටීම", "පාර වැරදීම"], "correct_index": 1, "timestamp": 14000
                    },
                    {
                        "id": "qB5", "text": "තමන්ව මැරීමට ආ දඩයක්කාරයා වැටී සිටිනු දැක මුවා කළේ කුමක්ද?",
                        "options": ["සතුටු වී පැන ගියා", "ඔහුට උදව් කිරීමට ඉදිරිපත් වුණා", "සැඟවී සිටියා", "ගල් ගැසුවා"], "correct_index": 1, "timestamp": 14000
                    },
                    {
                        "id": "qB6", "text": "මුවා දඩයක්කාරයාව බේරා ගත්තේ කෙසේද?",
                        "options": ["තමන්ගේ අං තට්ටුව හෝ වැලක් ආධාරයෙන්", "කෑගසා මිනිසුන් කැඳවීමෙන්", "හිනා වීමෙන්", "පැන යාමෙන්"], "correct_index": 0, "timestamp": 14000
                    },
                    {
                        "id": "qB7", "text": "බේරුණු පසු දඩයක්කාරයා කළේ කුමක්ද?",
                        "options": ["මුවාට විදීමට තැත් කළා", "දුන්න බිම දමා මුවාගෙන් සමාව ඉල්ලුවා", "දුවන්න පටන් ගත්තා", "මුවාව අල්ලා ගත්තා"], "correct_index": 1, "timestamp": 20000
                    },
                    {
                        "id": "qB8", "text": "මුවා දඩයක්කාරයාට සමාව දුන්නේ ඇයි?",
                        "options": ["මුවා ඉතා කරුණාවන්ත නිසා", "දඩයක්කාරයා කෑම දුන් නිසා", "බය වූ නිසා", "රජු අණ කළ නිසා"], "correct_index": 0, "timestamp": 20000
                    },
                    {
                        "id": "qB9", "text": "දඩයක්කාරයා තමන්ගේ දුන්න විසි කළේ ඇයි?",
                        "options": ["එය කැඩුණු නිසා", "තවදුරටත් සතුන් මැරීමට අකමැති වූ නිසා", "බර වැඩි නිසා", "අලුත් එකක් ගැනීමට"], "correct_index": 1, "timestamp": 20000
                    },
                    {
                        "id": "qB10", "text": "මුවාගෙන් ලැබුණු පාඩම නිසා දඩයක්කාරයා කළේ කුමක්ද?",
                        "options": ["සතුන්ට ආදරය කරමින් ඔවුන් ආරක්ෂා කිරීම", "වෙනත් රැකියාවක් සෙවීම", "වනාන්තරය ගිනි තැබීම", "රජුට පැමිණිලි කිරීම"], "correct_index": 0, "timestamp": 25000
                    },
                    {
                        "id": "qB11", "text": "දඩයක්කාරයා සහ මුවා අතර ඇති වූ සම්බන්ධය කුමක්ද?",
                        "options": ["සතුරන් වීම", "හොඳ මිතුරන් වීම", "එකිනෙකා අමතක කිරීම", "රජුගේ සේවකයන් වීම"], "correct_index": 1, "timestamp": 25000
                    },
                    {
                        "id": "qB12", "text": "මෙම කතාවෙන් අපට ලැබෙන උතුම් පාඩම කුමක්ද?",
                        "options": ["දඩයම් කිරීම හොඳ බව", "වෛරයට වඩා කරුණාව බලවත් බව", "මුවන්ට බය විය යුතු බව", "තනිවම වනාන්තරයට නොයා යුතු බව"], "correct_index": 1, "timestamp": 25000
                    },
                    {
                        "id": "qB13", "text": "දඩයක්කාරයා අනතුරේ වැටුණු විට ඔහුට පිහිට වූයේ කවුද?",
                        "options": ["රජතුමා", "රන්වන් මුවා", "අනෙක් දඩයක්කාරයෝ", "කිසිවෙක් නැත"], "correct_index": 1, "timestamp": 30000
                    },
                    {
                        "id": "qB14", "text": "මුවාගේ උතුම් ගතිය කුමක්ද?",
                        "options": ["වේගයෙන් දිවීම", "තමන්ව මැරීමට ආ අයෙකුට වුවද උදව් කිරීම", "සැඟවී සිටීම", "ලස්සනට සිටීම"], "correct_index": 1, "timestamp": 30000
                    },
                    {
                        "id": "qB15", "text": "කතාව අවසානයේ වනාන්තරය කෙබඳු තැනක් වූවාද?",
                        "options": ["බය හිතෙන තැනක්", "සතුන්ට නිදහසේ සිටිය හැකි සාමකාමී තැනක්", "පාලු තැනක්", "නගරයක්"], "correct_index": 1, "timestamp": 30000
                    }
                ]
            }
        },
        "interactions": {
            "choice_popup": {
                "type": "decision",
                "text": "ඔබේ තේරීම!\nඔබ කැමති රන්වන් මුවා කුමක් කරනවාට ද?",
                "options": [
                    {"text": "A) වනාන්තරයේ ඇවිදීම", "next_segment_id": "branch_a"},
                    {"text": "B) දඩයක්කාරයෙකු දැකීම", "next_segment_id": "branch_b"}
                ]
            }
        }
    }
    
    # Insert or update the story
    await collection.update_one(
        {"_id": "story_deer"}, 
        {"$set": deer_story}, 
        upsert=True
    )
    print("Deer story successfully injected into MongoDB!")

if __name__ == "__main__":
    asyncio.run(seed_deer_story())

