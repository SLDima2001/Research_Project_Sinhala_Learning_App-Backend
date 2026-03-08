import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "sinhala_learning_app"

async def seed_andare_story():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    collection = db["stories"]
    
    andare_story = {
        "_id": "story_andare",
        "id": "story_andare",
        "title": "අන්දරේ සීනි කාපු හැටි (Andare Eats Sugar)",
        "type": "video_interactive",
        "segments": {
            "main_segment": {
                "video_id": "Andare.mp4",
                "start_time": 0,
                "end_time": 300000, # Large enough to hit the end
                "next_segment_id": "end_screen",
                "question_timestamps": [30000, 70000, 120000, 180000, 200000],
                "question_pool": [
                    # Bucket 1: Intro & Setting (30000)
                    {"id": "q1_1", "text": "රජ මාලිගාව ඉදිරිපිට වේලෙන්න දමා තිබුණේ කුමක්ද?", "options": ["සහල්", "සීනි", "ලුණු"], "correct_index": 1, "timestamp": 30000},
                    {"id": "q1_2", "text": "සීනි ටික වේලෙන්න දමා තිබුණේ කුමක් මතද?", "options": ["පැදුරක් මත", "ලෑල්ලක් මත", "රෙද්දක් මත"], "correct_index": 0, "timestamp": 30000},
                    {"id": "q1_3", "text": "සීනි දුටු සැණින් අන්දරේට ඇති වූ ආශාව කුමක්ද?", "options": ["සීනි අහුරක් කටේ දාගන්න", "සීනි මල්ලක් ගෙදර ගෙනියන්න", "සීනි විකුණන්න"], "correct_index": 0, "timestamp": 30000},
                    {"id": "q1_4", "text": "මෙම කතාව සිදුවන්නේ කොහේද?", "options": ["වනයක", "කුඹුරක", "රජ මාලිගාවක"], "correct_index": 2, "timestamp": 30000},
                    {"id": "q1_5", "text": "කතාවේ මුලින්ම අන්දරේ සීනි කෑමට බය වුණේ ඇයි?", "options": ["රජතුමා දඬුවම් කරයි කියා", "රජතුමා ඔහුට සීනි එපා කිව් නිසා", "සීනිවලට පස් කලවම් වී ඇති නිසා"], "correct_index": 0, "timestamp": 30000},

                    # Bucket 2: The King's Lie (70000)
                    {"id": "q2_1", "text": "රජතුමා සීනිවලට කිව්වේ කුමක් කියාද?", "options": ["සුදු පාට පස් ජාතියක්", "සුදු පාට වැලි", "සුදු පාට පිටි"], "correct_index": 0, "timestamp": 70000},
                    {"id": "q2_2", "text": "රජතුමා සීනි \"පස්\" කියලා කිව්වේ ඇයි?", "options": ["ඇත්තටම ඒවා පස් නිසා", "අන්දරේ සීනි කයි කියලා බයට", "අන්දරේට විහිළු කිරීමට"], "correct_index": 1, "timestamp": 70000},
                    {"id": "q2_3", "text": "අන්දරේ රජතුමාට ආමන්ත්රණය කළේ කෙසේද?", "options": ["දේවයන් වහන්ස", "මහරජතුමනි", "යාළුවේ"], "correct_index": 0, "timestamp": 70000},
                    {"id": "q2_4", "text": "සීනි පස් කියලා දැනගත්තාම අන්දරේ රජුට දුන් පිළිතුර කුමක්ද?", "options": ["\"මට වැරදෙන්න ඇති දේවයන් වහන්ස\"", "\"නැහැ රජතුමනි මේවා සීනි\"", "\"මට මේවා එපා\""], "correct_index": 0, "timestamp": 70000},
                    {"id": "q2_5", "text": "රජතුමා \"අන්දරේට සීනියි පස්සයි අඳුරගන්න බැරි වුණාද?\" කියා ඇහුවේ ඇයි?", "options": ["අන්දරේට විහිළු කිරීමට", "අන්දරේ මෝඩයෙක් කියලා හිතපු නිසා", "අන්දරේගේ ඇස් පෙනීම දුර්වල නිසා"], "correct_index": 0, "timestamp": 70000},

                    # Bucket 3: Andare's Plan (120000)
                    {"id": "q3_1", "text": "අන්දරේ සීනි කෑමට මාලිගාවට එක්කගෙන ආවේ කාවද?", "options": ["බිරිඳව", "පුතාව", "යාළුවෙක්ව"], "correct_index": 1, "timestamp": 120000},
                    {"id": "q3_2", "text": "අන්දරේ සහ පුතා සීනි කන අතරතුර කළේ කුමක්ද?", "options": ["සින්දු කිව්වා", "ඉකි ගසමින් ඇඬුවා", "නර්තනයක යෙදුණා"], "correct_index": 1, "timestamp": 120000},
                    {"id": "q3_3", "text": "අන්දරේ සහ පුතා ඇඬුවේ කා ගැන මතක් කරමින්ද?", "options": ["අත්තම්මා ගැන", "අම්මා ගැන", "රජතුමා ගැන"], "correct_index": 0, "timestamp": 120000},
                    {"id": "q3_4", "text": "අන්දරේ ඇඬුවේ ඇයි?", "options": ["රජුව රැවටීමට", "ඇත්තටම දුක හිතුණ නිසා", "සීනි නැති නිසා"], "correct_index": 0, "timestamp": 120000},
                    {"id": "q3_5", "text": "අන්දරේගේ සැලසුමට උදව් කළේ කවුද?", "options": ["රජතුමා", "පුතා", "අත්තම්මා"], "correct_index": 1, "timestamp": 120000},

                    # Bucket 4: The Outcome (180000)
                    {"id": "q4_1", "text": "සීනි කෑම නවත්වන්න රජුට බැරි වුණේ ඇයි?", "options": ["පැදුරේ තියෙන්නේ පස් කියලා රජුම කලින් කියපු නිසා", "අන්දරේ රජුට වඩා ශක්තිමත් නිසා", "රජතුමා එතන නැති නිසා"], "correct_index": 0, "timestamp": 180000},
                    {"id": "q4_2", "text": "අන්දරේ සහ පුතා සීනි කෑවේ කොහොමද?", "options": ["ඉතා ටිකක් පමණක්", "හිතේ හැටියට", "හොර රහසේ"], "correct_index": 1, "timestamp": 180000},
                    {"id": "q4_3", "text": "අන්දරේගේ ක්රියාව දුටු රජතුමාට ඇති වූ හැඟීම කුමක්ද?", "options": ["හිනාව නවත්වගන්න බැරි වුණා", "අධික කේන්තියක්", "පුදුමයක්"], "correct_index": 0, "timestamp": 180000},
                    {"id": "q4_4", "text": "රජතුමා අන්දරේට කතා කළේ කුමන නමකින්ද?", "options": ["හොරා", "කවටයා", "ඇමති"], "correct_index": 1, "timestamp": 180000},
                    {"id": "q4_5", "text": "අන්දරේ රජුට පැවසුවේ තමන් මොනවා කනවා කියාද?", "options": ["සීනි", "රජතුමා කියපු පස්", "වැලි"], "correct_index": 1, "timestamp": 180000},

                    # Bucket 5: Moral & Ending (200000)
                    {"id": "q5_1", "text": "අන්දරේ බුද්ධිමත් කියලා පෙනෙන්නේ ඇයි?", "options": ["ඔහු ලස්සනට ඇඬූ නිසා", "රජුගේ බොරුවෙන්ම රජුව රැවටූ නිසා", "ඔහු වේගයෙන් සීනි කෑ නිසා"], "correct_index": 1, "timestamp": 200000},
                    {"id": "q5_2", "text": "අන්දරේ \"මට වැරදෙන්න ඇති දේවයන් වහන්ස\" කිව්වේ ඇයි?", "options": ["රජුගේ බොරුව තහවුරු කරන්න", "ඇත්තටම වැරදුණ නිසා", "බයට"], "correct_index": 0, "timestamp": 200000},
                    {"id": "q5_3", "text": "අවසානයේ රජතුමා අන්දරේ ගැන කිව්වේ කුමක්ද?", "options": ["අන්දරේ වැනි කවටයෙක් නැවත හමු නොවන බව", "අන්දරේට දඬුවම් දිය යුතු බව", "අන්දරේ මෝඩයෙක් බව"], "correct_index": 0, "timestamp": 200000},
                    {"id": "q5_4", "text": "මෙම කතාවේ ප්රධාන චරිතය කවුද?", "options": ["රජතුමා", "අන්දරේ", "අත්තම්මා"], "correct_index": 1, "timestamp": 200000},
                    {"id": "q5_5", "text": "මෙම කතාවෙන් දෙන හොඳම පාඩම කුමක්ද?", "options": ["බොරු කීමෙන් තමන්ම අමාරුවේ වැටෙන බව", "සීනි ගොඩක් කෑම සෞඛ්යයට නරක බව", "රජවරුන්ට බය විය යුතු බව"], "correct_index": 0, "timestamp": 200000}
                ]
            }
        },
        "interactions": {}
    }
    
    # Insert or update the story
    await collection.update_one(
        {"_id": "story_andare"}, 
        {"$set": andare_story}, 
        upsert=True
    )
    print("Andare story successfully injected into MongoDB!")

if __name__ == "__main__":
    asyncio.run(seed_andare_story())
