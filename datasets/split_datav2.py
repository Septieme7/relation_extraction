"""
用brat_trans_Relation.py脚本生成的所有known.jsonl, unknown.jsonl 分割成训练集与验证集
known.jsonl, uknown.jsonl  ->  train.jsonl, val.jsonl
(原本的split_data.py脚本是将txt文件分割成train.jsonl, val.jsonl)  txt -> train.jsonl, val.jsonl
"""
import os
import re
import json
import random

random.seed(12345)

here = os.path.dirname(os.path.abspath(__file__))


def convert_data(line):
    head_name, tail_name, relation, text = re.split(r'\t', line)
    match_obj1 = re.search(head_name, text)
    match_obj2 = re.search(tail_name, text)
    if match_obj1 and match_obj2:  # 姑且使用第一个匹配的实体的位置
        head_pos = match_obj1.span()
        tail_pos = match_obj2.span()
        item = {
            'h': {
                'name': head_name,
                'pos': head_pos
            },
            't': {
                'name': tail_name,
                'pos': tail_pos
            },
            'relation': relation,
            'text': text
        }
        return item
    else:
        return None


def save_data(lines, file):
    print('保存文件：{}'.format(file))
    unknown_cnt = 0
    with open(file, 'w', encoding='utf-8') as f_out:
        for line in lines:
            item = convert_data(line)
            if item is None:
                continue
            if item['relation'] == 'unknown':
                unknown_cnt += 1
            json_str = json.dumps(item, ensure_ascii=False)
            f_out.write('{}\n'.format(json_str))
    print('unknown的比例：{}/{}={}'.format(unknown_cnt, len(lines), unknown_cnt / len(lines)))


def split_data(file):
    file_dir = os.path.dirname(file)
    train_file = os.path.join(file_dir, 'train.jsonl')
    val_file = os.path.join(file_dir, 'val.jsonl')
    with open(file, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()
    lines = [line.strip() for line in lines]
    random.shuffle(lines)
    lines_len = len(lines)
    train_lines = lines[:lines_len * 7 // 10]
    val_lines = lines[lines_len * 7 // 10:]
    save_data(train_lines, train_file)
    save_data(val_lines, val_file)

def split_json(file, known):
    with open(file, 'r', encoding='utf-8') as f_in:
        lines = f_in.readlines()
    lines = [line.strip() for line in lines]
    random.shuffle(lines)
    lines_len = len(lines)
    train_lines = lines[:lines_len * 7 // 10]
    val_lines = lines[lines_len * 7 // 10:]

    if known == True:
        train_file = open('train_known_guwen.jsonl', 'w')
        val_file = open('val_known_guwen.jsonl', 'w')
    else:
        train_file = open('train_unknown_guwen.jsonl', 'w')
        val_file = open('val_unknown_guwen.jsonl', 'w')
    for line in train_lines:
        train_file.write(line+'\n')
    for line in val_lines:
        val_file.write(line+'\n')




def main():
    # all_data = os.path.join(here, 'all_data.txt')
    # split_data(all_data)
    split_json('../brat标注转训练数据/known.jsonl', True)  # known的部分
    split_json('../brat标注转训练数据/unknown.jsonl', False)  # unknown的部分



if __name__ == '__main__':
    main()
