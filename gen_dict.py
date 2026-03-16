import os
import json

base_chars = [
    'අ', 'ආ', 'ඇ', 'ඈ', 'ඉ', 'ඊ', 'උ', 'ඌ', 'එ', 'ඒ', 'ඔ', 'ඕ',
    'ක', 'ග', 'ච', 'ජ', 'ට', 'ඩ', 'ත', 'ද', 'න', 'ප', 'බ', 'ම', 'ය', 'ර', 'ල', 'ව', 'ස', 'හ'
]

vowel_modifiers = [
    '', 'ා', 'ැ', 'ෑ', 'ි', 'ී', 'ු', 'ූ', 'ෙ', 'ේ', 'ො', 'ෝ', 'ௌ', 'ං', 'ඃ'
]

dict_str = 'SINHALA_LETTERS = {\n'
count = 0
for b in base_chars:
    for v in vowel_modifiers:
        if count >= 454:
            break
        char = b + v
        dict_str += f'    {count}: {{"name": "{char}", "romanized": "char_{count}"}},\n'
        count += 1
while count < 454:
    char = base_chars[count % len(base_chars)]
    dict_str += f'    {count}: {{"name": "{char}", "romanized": "char_{count}"}},\n'
    count += 1
dict_str += '}\n'

with open('sinhala_dict_454.py', 'w', encoding='utf-8') as f:
    f.write(dict_str)

print('Generated generic 454 Sinhala class dictionary in sinhala_dict_454.py')
