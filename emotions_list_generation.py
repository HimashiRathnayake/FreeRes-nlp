import os
import re

with (open(os.path.join("files/emotions.txt"), 'r', encoding='utf-8') as file):
    emotions_dict = {}
    emotion_list_2 = []

    for line in file:
        values = [value.strip() for value in line.split(',')]
        for item in values:
            match = re.match(r'^(.*?)\s*\((.*?)\)$', item)
            if match:
                key, value = match.groups()
                key, value = key.strip(), int(value.strip())
            else:
                key, value = item.strip(), 1
            if len(key.split(" ")) == 1:
                if key in emotions_dict:
                    emotions_dict[key] = emotions_dict[key] + value
                else:
                    emotions_dict[key] = value
            else:
                if key not in emotion_list_2:
                    emotion_list_2.append(key)
    sorted_dict = dict(sorted(emotions_dict.items(), key=lambda item: item[1], reverse=True))


with open(os.path.join("files/word_lists/2.txt"), 'w', encoding='utf-8') as file:
    for item in sorted_dict.keys():
        file.write(f'{item}   {sorted_dict[item]}\n')
with open(os.path.join("files/word_lists/3.txt"), 'w', encoding='utf-8') as file:
    for item in emotion_list_2:
        file.write(f'{item}\n')