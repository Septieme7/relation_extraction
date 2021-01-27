'''
已有空格分割的文本文件，标签文件，需要将其转成brat的ann文件，其对应的txt为原生长度，已知
预测的时候有规定最大长度，也就是说最后输出的时候每行一定不会超过该长度
'''
'''
得到从index位置开始的这个实体的长度
lst：
index：实体开始位置
'''
def get_entity_len(lst, index):
    max_len = len(lst)
    res = 1
    entity = lst[index][2:]
    for i in range(index+1, max_len):
        entity2 = lst[i][2:]   # 得到实体类别
        bi = lst[i][0]  # B/I
        if entity != entity2 or bi != 'I':
            break
        else:
            res += 1
    return res


'''
得到这个字在第几行，也就是用来计算\n个数
len_list: 每一行的长度list，不包括\n
index: 字的绝对索引
'''
def getline(len_list, index):
    cur = 0
    i = 0
    while(cur <= index):
        cur += len_list[i]
        i += 1
    return i-1

if __name__ == '__main__':

    std_len = 128

    origin_text = open('../data_marked/test/juan1_wudibenji_di1.txt')  # 最原本的文本文件 也就是需要还原的样子
    label = open('../output_label.txt', 'r')  # 预测的label文件
    ann = open('new_predict_result.ann', 'w')  # 根据预测结果要写的新的ann文件

    len_list = []  # 每一行的原始长度list,不包括\n
    all_text = ''
    for line in origin_text.readlines():
        line = line.strip()
        len_list.append(len(line))
        all_text += str(line)

    i = 0  # 当前的索引位置
    entt_start_pos = []  # 先遍历，记录所有实体开始的地方，这里不包括\n，这个list用来定位实体的内容
    pos = []  # 包括\n，也就是最终需要写到文件里面的位置，这里是由于\n所以需要pos这个list
    entt_len = []
    all_label = []  # 合并所有的标签 不分行
    for line in label.readlines():
        line = line.strip()
        label_lst = line.split(' ')
        for j,l in enumerate(label_lst):
            if(l[0] == 'B'):
                entt_start_pos.append(i)
            i+=1
        all_label.extend(label_lst)
    print(entt_start_pos)
    print(len(entt_start_pos))
    print(all_label)


    print(all_text)

    for i in entt_start_pos:
        pos.append(i+getline(len_list, i))  # 用entt_start_pos加上原生文件中的\n个数 就是最后要写到文件里的位置
    print(pos)

    # 实体长度计算
    for i in entt_start_pos:
        entt_len.append(get_entity_len(all_label, i))
    print(entt_len)

    # 写入文件
    for i in range(len(entt_start_pos)):
        start = entt_start_pos[i]
        end = start + entt_len[i]
        ett_type = all_label[start]  # 实体类别
        ett = all_text[start:end]
        l = entt_len[i]  # 实体长度
        ann.write('T'+str(i+1)+'	'+ett_type+' '+str(pos[i])+' '+str(pos[i]+l)+' '+ett+'\n')
