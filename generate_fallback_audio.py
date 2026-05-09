import os
from gtts import gTTS

fallback_sentences = [
    {"id": "off_001", "text": "ආයුබෝවන් සුභ දවසක්"},
    {"id": "off_002", "text": "ඔබ කොහෙද යන්නේ"},
    {"id": "off_003", "text": "මගේ නම සිතාරා"},
    {"id": "off_004", "text": "ඔබට ස්තූතියි"},
    {"id": "off_005", "text": "සිංහල ඉගෙනීම ප්‍රසාදජනකයි"},
    {"id": "off_006", "text": "ගෙදර යමු"},
    {"id": "off_007", "text": "ඔයා කොහොමද"},
    {"id": "off_008", "text": "අම්මා හොඳ කෑම හදනවා"},
    {"id": "off_009", "text": "ලංකාව ලස්සන රටක්"},
    {"id": "off_010", "text": "හිරු එළිය ලස්සනයි"},
    {"id": "off_011", "text": "කලාව ජීවිතය සුන්දර කරයි"},
    {"id": "off_012", "text": "මම ළමයෙක්"},
    {"id": "off_013", "text": "මට පොත් ආසයි"},
    {"id": "off_014", "text": "කුරුල්ලෝ ගී කියනවා"},
    {"id": "off_015", "text": "පාසල ළඟ ගස් තිබෙනවා"}
]

output_dir = "fallback_audio"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

import imageio_ffmpeg
import subprocess
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

for sentence in fallback_sentences:
    file_id = sentence["id"]
    text = sentence["text"]
    temp_mp3 = os.path.join(output_dir, f"{file_id}_temp.mp3")
    final_wav = os.path.join(output_dir, f"{file_id}.wav")
    
    print(f"Generating {final_wav}...")
    tts = gTTS(text, lang='si')
    tts.save(temp_mp3)
    
    
    subprocess.run([
        ffmpeg_exe, "-y", "-i", temp_mp3, "-ar", "16000", "-ac", "1", final_wav
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    os.remove(temp_mp3)

print("Done generating fallback audio.")
