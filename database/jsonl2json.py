
import jsonlines
import json

with jsonlines.open('../brat标注转训练数据/known.jsonl', "r") as rfd:
    with open('known.json', "w", encoding='utf-8') as wfd:
        for data in rfd:
            json.dump(data, wfd, indent=4, ensure_ascii=False)

# 2csv link: https://json-csv.com
