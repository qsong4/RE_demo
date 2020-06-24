import os, sys
import pandas as pd
import random
from tqdm import tqdm
cur_dir = os.path.dirname(__file__)

#合并用户数据以及保险数据
def cmobine_userIns(ufile, insfile, clickfile, outfile):
    #得到保险的字典
    ins_dict = dict()
    ins = pd.read_csv(insfile, sep="\t", header=0)
    for index, row in ins.iterrows():
        id = row["InsID"]
        # ins_dict[id] = row.drop("InsID").tolist()
        ins_dict[id] = [str(i) for i in row.tolist()]
        # print(ins_dict)
    #得到用户字典
    user_dict = dict()
    user = pd.read_csv(ufile, sep="\t", header=0)
    for index, row in user.iterrows():
        id = row["UID"]
        # user_dict[id] = row.drop("ID").tolist()
        user_dict[id] = [str(i) for i in row.tolist()]
        # print(user_dict)

    columns = ["ID"]+user.columns.values.tolist()+ins.columns.values.tolist()+["target"]
    # print(len(columns))

    with open(clickfile, 'r') as fr, open(outfile, 'w') as fw:
        fw.write("\t".join(columns)+"\n")
        i = 0
        for line in tqdm(fr):

            content = line.strip().split("\t")
            uid = int(content[0])
            insid = int(content[1])
            isclick = content[2]
            u_feats = user_dict[uid]
            i_feats = ins_dict[insid]
            # print(len(u_feats)+len(i_feats)+1)

            fw.write(str(i)+"\t"+"\t".join(u_feats+i_feats)+"\t"+isclick+"\n")
            i+=1


#生成用户点选记录
def user2ins(userfile, insfile, outfile):
    userfeats = pd.read_csv(userfile, sep="\t", header=0)
    insfeats = pd.read_csv(insfile, sep="\t", header=0)
    insID = insfeats['InsID'].tolist()
    userID = userfeats['UID'].tolist()
    with open(outfile, 'w') as fw:
        for index, row in userfeats.iterrows():
            #每个人可能买0~4个保险
            num_ins = random.randint(0, 4)
            _tmp = []
            _uid = row['UID']
            for _ in range(num_ins):
                pos_insid = insID[random.randint(0,len(insID)-1)]
                if pos_insid not in _tmp:
                    _tmp.append(pos_insid)
                    fw.write(f"{_uid}\t{pos_insid}\t1\n")
            sub_insid = list(set(insID) - set(_tmp))
            _tmp = []
            for _ in range(num_ins*2):
                neg_insid = sub_insid[random.randint(0,len(sub_insid)-1)]
                if neg_insid not in _tmp:
                    _tmp.append(neg_insid)
                    fw.write(f"{_uid}\t{neg_insid}\t0\n")

# 生成用户信息
def generate_user_info(infile, outfile):
    occ_map = {0:"室内工作",1:"室外工作",2:"高危职业",3:"退休", 4:"学生", 5:"其它", 6:"医生", 8:"农民",12:"程序员"}
    _insurance = ["意外险","重疾险","医疗险","年金险","分红险","少儿险","定期寿险","其它","0","0","0"]
    _chuxing = ["爱旅游","公共交通","常开车","电动车","自行车","步行","0","0","0","0"]
    _shenghuo = ["加班多","睡觉晚","运动少","常喝酒","有烟瘾","0","0","0"]
    _health = ["失眠","尿酸高","三高人群","肠胃不好","颈椎不适","很健康","心脑血管疾病","0","0","0"]
    _shouru = ["低","中","高","0","0"]
    _daikuan = ["是", "否","0","0"]

    columns = ["UID", "性别", "年龄", "收入", "职业", "出行方式", "生活习惯", "健康情况", "是否贷款", "已购保险类型"]

    with open(infile, 'r') as fr, open(outfile, "w") as fw:
        fw.write("\t".join(columns) + "\n")
        for line in fr:
            content = line.strip().split("::")
            uid = content[0]
            gender = "男" if content[1] == "M" else "女"
            shouru = _shouru[random.randint(0,len(_shouru)-1)]
            _occ = content[3]
            if _occ in occ_map:
                occ = occ_map[_occ]
            else:
                occ = list(occ_map.values())[random.randint(0,len(occ_map.values())-1)]
            _age = int(content[2])
            if _age < 14:
                age = "幼儿"
            elif _age >=14 and _age < 35:
                age = "青年"
            elif _age >= 34 and _age < 50:
                age = "中年"
            else:
                age = "老年"

            chuxing = _chuxing[random.randint(0, len(_chuxing) - 1)]
            shenghuo = _shenghuo[random.randint(0, len(_shenghuo) - 1)]
            health = _health[random.randint(0, len(_health) - 1)]
            daikuan = _daikuan[random.randint(0, len(_daikuan) - 1)]
            insurance = _insurance[random.randint(0, len(_insurance) - 1)]

            features = [uid,gender,age,shouru,occ,chuxing,shenghuo,health,daikuan,insurance]
            # print(features)
            fw.write("\t".join(features)+"\n")


def excel2csv(excel, outfile, sheetname=0, header=0, columns=[]):
    df = pd.read_excel(excel, sheet_name=sheetname, header=header)
    col = df.columns.values.tolist()[:10]
    col.insert(0, "InsID")
    print(col)
    with open(outfile, 'w') as fw:
        fw.write("\t".join(col)+"\n")
        for index, row in df.iterrows():
            cs = []
            cs.append(str(index))
            for c in columns:
                cs.append(str(row[c]))
            fw.write("\t".join(cs)+"\n")
    print("DONE")

def pre(infile, infile2, outfile):
    type_map = {}
    with open(infile2, "r") as fr:
        for line in fr:
            content = line.strip().split("\t")
            ins = content[0]
            _type = content[1]
            if ins in type_map:
                type_map[ins].append(_type)
            else:
                type_map[ins] = [_type]

    with open(infile, "r") as fr, open(outfile, "w") as fw:
        for line in fr:
            content = line.strip().split("\t")
            content = content[:-1]
            ins = content[0]
            if ins in type_map:
                content.append("|".join(type_map[ins]))
            else:
                content.append("0")
            fw.write("\t".join(content) + "\n")


if __name__ == '__main__':
    # columns = ["保险名","类型","价格","适合年龄","保单形式","销售范围","适用疾病","适用职业","缴费方式","关键词"]
    # pre("./insurance_label.csv", "./rel_type.csv", "./insurance_feature.csv")
    # excel2csv("./doc/保险属性信息.xlsx", "./insurance_data.csv", columns=columns)
    # generate_user_info("./users_raw.csv", "./users_feats.csv")
    # user2ins("./users_feats.csv", "./insurance_data.csv", "./click.csv")
    cmobine_userIns("./users_feats.csv", "./insurance_data.csv", "./click.csv", "combine_features.csv")
