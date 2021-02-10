import pandas as pd
import numpy as np
import re
import os
# 得到目录下的全部文件名
def getallname():
    known_name = []
    for root, dirs, files in os.walk("known", topdown=False):
        for file in files:
            n = file.split(".")[0]
            if len(n) != 0:
                if n not in known_name:
                    known_name.append(n)

    unknown_name = []
    for root, dirs, files in os.walk("unknown", topdown=False):
        for file in files:
            n = file.split(".")[0]
            if len(n) != 0:
                if n not in unknown_name:
                    unknown_name.append(n)

    artical_name = []
    for root, dirs, files in os.walk("artical", topdown=False):
        for file in files:
            n = file.split(".")[0]
            if len(n) != 0:
                if n not in artical_name:
                    artical_name.append(n)

    return known_name, unknown_name, artical_name

def if_split(p1, p2, text):
    '''
    判断实体1与实体2之间是否有句号
    :param p1:
    :param p2:
    :param text:
    :return:
    '''
    result = '。' in text[p1:p2]
    return result

def find_end(p, artical):
    '''
    找到一个实体末尾距离其最近的一个句号的位置
    :param p:
    :param text:
    :return:
    '''
    text = artical[p:]
    p_ = text.index("。") + p
    return p_

if __name__ == '__main__':

    known_name, unknown_name, artical_name = getallname()
    for file_count in range(len(known_name)):
        row_name = "./unknown/" + unknown_name[file_count] + '.jsonl'
        row_data = pd.read_csv(row_name, header=None, delimiter='\\s+', encoding='utf-8')
        text_name = "./artical/" + artical_name[file_count] + '.txt'
        with open(text_name, 'r', encoding='utf-8') as f:
            artical = f.read()
        known_file_name = "./known/" + known_name[file_count] + '.jsonl'
        know_data = pd.read_csv(known_file_name, header=None, delimiter='\\s+', encoding='utf-8')

        text = row_data.iloc[:, -1]

        # t1包含第一个实体
        t1 = row_data.iloc[:, 2]
        t1_pos_head = row_data.iloc[:, 4]
        t1_pos_tail = row_data.iloc[:, 5]
        t1_type = row_data.iloc[:, 7]
        for i in range(len(t1)):
            t1[i] = t1[i][:-1]
            t1_pos_head[i] = int(t1_pos_head[i][1:-1])
            t1_pos_tail[i] = int(t1_pos_tail[i][:-2])
            t1_type[i] = t1_type[i][:-2]
            text[i] = text[i][:-1]

        # t2包含第二个实体
        t2 = row_data.iloc[:, 10]
        t2_pos_head = row_data.iloc[:, 12]
        t2_pos_tail = row_data.iloc[:, 13]
        t2_type = row_data.iloc[:, 15]
        for i in range(len(t2)):
            t2[i] = t2[i][:-1]
            t2_pos_head[i] = int(t2_pos_head[i][1:-1])
            t2_pos_tail[i] = int(t2_pos_tail[i][:-2])
            t2_type[i] = t2_type[i][:-2]

        '''
        # 保存每一行的关系，在读完每一行时输出一次
        relation_temp = []
        # 保存每一行的实体,按顺序排列
        t_temp = []
        '''

        # 记录text总长度
        total_len = 0

        # 初始化实体-head dataframe，然后每次换行更新一次
        t_h_df = pd.DataFrame(columns=['t', 'head', 'type'])
        t_list = []
        h_list = []
        type_list = []

        # 遍历unknown，生成实体
        for i in range(1, len(text)):
            if text[i] != text[i - 1]:
                # 每次窗口滑动，更新total_len的值，每次更新的值为text起始位置在原文的位置
                match = re.search(text[i], artical)
                total_len = match.start()

            text1 = text[i]
            t_list.append(t1[i])
            t_list.append(t2[i])

            h_list.append(t1_pos_head[i] + total_len)
            h_list.append(t2_pos_head[i] + total_len)

            type_list.append(t1_type[i])
            type_list.append(t2_type[i])

        '''        t_h_df = pd.DataFrame(columns=['t', 'head'])
                t_list = []
                h_list = []'''
        t_h_df['t'] = t_list
        t_h_df['head'] = h_list
        t_h_df['type'] = type_list

        # 将每个实体，按照其head位置排序
        t_h_df = t_h_df.sort_values(by='head', axis=0, ascending=True)
        # 去重
        t_h_df = t_h_df.drop_duplicates()
        # 重置索引
        t_h_df = t_h_df.reset_index(drop=True)
        print("实体列表")
        print(t_h_df)

        # 下面进行关系的标注

        # 如果上一个实体和下一个实体之间，存在"。",则认为应该在该实体之后输出一行关系
        # 用实体的起始位置来代替该实体，所以两个实体之间存在关系，即为两个起始位置之间存在关系

        # r包含关系
        r = know_data.iloc[:, 17]
        for i in range(len(r)):
            r[i] = r[i][:-1]

        # t1包含第一个实体
        r_text = know_data.iloc[:, -1]

        r_t1 = know_data.iloc[:, 2]
        r_t1_pos_head = know_data.iloc[:, 4]
        for i in range(len(r_t1)):
            r_t1[i] = r_t1[i][:-1]
            r_t1_pos_head[i] = int(r_t1_pos_head[i][1:-1])
            r_text[i] = r_text[i][:-1]

        # t2包含第二个实体
        r_t2 = know_data.iloc[:, 10]
        r_t2_pos_head = know_data.iloc[:, 12]

        for i in range(len(r_t2)):
            r_t2[i] = r_t2[i][:-1]
            r_t2_pos_head[i] = int(r_t2_pos_head[i][1:-1])

        r_h_df = pd.DataFrame(columns=['head1', 'head2', 'relation'])
        # 遍历known，生成实体与关系
        r_total_len = 0
        head1 = []
        head2 = []
        r_list = []
        for i in range(1, len(r_text)):
            if r_text[i] != r_text[i - 1]:
                # 每次窗口滑动，更新total_len的值，每次更新的值为text起始位置在原文的位置
                match = re.search(r_text[i], artical)
                r_total_len = match.start()
            r_list.append(r[i])
            head1.append(r_t1_pos_head[i] + r_total_len)
            head2.append(r_t2_pos_head[i] + r_total_len)

        r_h_df['head1'] = head1
        r_h_df['head2'] = head2
        r_h_df['relation'] = r_list

        print("关系列表\n", '---------------------------')
        print(r_h_df)

        # 初始化关系计数R, 用于关系的迭代
        r_count = 0
        output_name = "./result_brat/" + artical_name[file_count] + '.ann'
        with open(output_name, "w+", encoding="utf-8") as f:
            for i in range(len(t_h_df)):
                t_index_ = 'T' + str(i + 1)
                f.write(t_index_)
                f.write("\t")
                f.write(t_h_df['type'][i])
                f.write(" ")
                f.write(str(t_h_df['head'][i]))
                f.write(' ')
                end_ = t_h_df['head'][i] + len(t_h_df['t'][i])
                f.write(str(end_))
                f.write("\t")
                f.write(t_h_df['t'][i])
                f.write("\n")

                # 下面开始增加关系
                # 查找距离该实体位置最近的句号位置
                p_ = t_h_df['head'][i]

                near_end_ = find_end(p_, artical)
                r_head_ = max(r_h_df['head1'][r_count], r_h_df['head2'][r_count])

                # 如果当前实体的最近句号的位置，已经大于关系列表中靠后的实体的位置，说明在这一行结束需要插入关系
                if near_end_ >= r_head_:

                    # 寻找第i个实体和第i+1个实体之间，是否有句号
                    flag = 0
                    if i != (len(t_h_df) - 1):
                        p1 = t_h_df['head'][i]
                        p2 = t_h_df['head'][i + 1]
                        # p3 = len(t_h_df[t_h_df['head'] == p2].iloc[0,0]) + p2
                        if if_split(p1, p2, artical):
                            flag = 1
                    # 如果两个实体之间存在句号，则说明要换行，每当换行时，标一次关系
                    if flag == 1:
                        while r_head_ <= near_end_:
                            if r_count >= (len(r_h_df) - 1):
                                break
                            r_index_ = 'R' + str(r_count + 1)
                            f.write(r_index_)
                            f.write("\t")

                            f.write(r_h_df['relation'][r_count])
                            f.write(" ")
                            arg1 = 'Arg1:'
                            temp = t_h_df[t_h_df['head'] == r_h_df['head1'][r_count]].index.values[0] + 1
                            str_temp = 'T' + str(temp)
                            arg1 = arg1 + str_temp

                            f.write(arg1)
                            f.write(' ')
                            arg2 = 'Arg2:'
                            temp2 = t_h_df[t_h_df['head'] == r_h_df['head2'][r_count]].index.values[0] + 1
                            str_temp2 = 'T' + str(temp2)
                            arg2 = arg2 + str_temp2
                            f.write(arg2)

                            f.write("\n")
                            r_count += 1
                            r_head_ = max(r_h_df['head1'][r_count], r_h_df['head2'][r_count])






