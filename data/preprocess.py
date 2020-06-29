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

def user2ins_plus(userfile, insfile, outfile):
    userfeats = pd.read_csv(userfile, sep="\t", header=0)
    insfeats = pd.read_csv(insfile, sep="\t", header=0)
    insID_all = insfeats['InsID'].tolist()
    price2ins = {}
    work2ins = {}
    type2ins = {}
    age2ins = {}
    for index, row in insfeats.iterrows():
        insID = row["InsID"]
        work = row["适用职业"]
        type = row["类型"]
        age = row["适合年龄"]
        price = row["价格"]

        if work in work2ins:
            work2ins[work].append(insID)
        else:
            work2ins[work] = [insID]
        if type in type2ins:
            type2ins[type].append(insID)
        else:
            type2ins[type] = [insID]
        if age in age2ins:
            age2ins[age].append(insID)
        else:
            age2ins[age] = [insID]
        if price in price2ins:
            price2ins[price].append(insID)
        else:
            price2ins[price] = [insID]
    print(price2ins)
    print(work2ins)
    print(type2ins)
    print(age2ins)
    with open(outfile, 'w') as fw:
        for index, row in userfeats.iterrows():
            _uid = row['UID']
            gender = row['性别']
            work = row["职业"]
            chuxing = row["出行方式"]
            age = row["年龄"]
            shouru = row["收入"]
            health = row["健康情况"]
            shenghuo = row["生活习惯"]
            _tmp = []
            num_ins = 0
            if gender == "女":
                # pos_insid_list.append("17")
                pos_insid = "17"
                _tmp.append(pos_insid)
                fw.write(f"{_uid}\t{pos_insid}\t1\n")

            pos_insid_list_shouru = []
            if "高" in shouru:
                ins_list = price2ins["高"]
                pos_insid_list_shouru = ins_list
            if "中" in shouru:
                ins_list = price2ins["中"]
                pos_insid_list_shouru = ins_list
            if "低" in shouru:
                ins_list = price2ins["低"]
                pos_insid_list_shouru = ins_list

            pos_insid_list_work = []
            if "高危" in work:
                ins_list = work2ins["高危工作"]
                pos_insid_list_work = ins_list
            if "室外" in work:
                ins_list = work2ins["室外工作"] + work2ins["室外工作|室内工作"] + work2ins["室外工作|室内工作|高危工作"]
                pos_insid_list_work = ins_list
            if "医生" in work:
                ins_list = type2ins["意外险"]
                pos_insid_list_work = ins_list

            pos_insid_list_work = list(set(pos_insid_list_work) - set(pos_insid_list_shouru))
            if len(pos_insid_list_work) > 0:
                pos_insid = pos_insid_list_work[random.randint(0, len(pos_insid_list_work) - 1)]
                fw.write(f"{_uid}\t{pos_insid}\t1\n")
                _tmp.append(pos_insid)

            pos_insid_list_age = []
            if "幼儿" in age:
                ins_list = age2ins["幼儿"]
                pos_insid_list_age = ins_list
            if "老年" in age:
                ins_list = age2ins["老年"]
                pos_insid_list_age = ins_list
            if "青年" in age:
                ins_list = age2ins["青年|中年"]
                pos_insid_list_age = ins_list
            if "中年" in age:
                ins_list = age2ins["青年|中年|老年"]
                pos_insid_list_age = ins_list

            pos_insid_list_age = list(set(pos_insid_list_age) - set(pos_insid_list_shouru))
            if len(pos_insid_list_age) > 0:
                pos_insid = pos_insid_list_age[random.randint(0, len(pos_insid_list_age) - 1)]
                fw.write(f"{_uid}\t{pos_insid}\t1\n")
                _tmp.append(pos_insid)

            pos_insid_list_chuxing = []
            if "电动车" in chuxing or "常开车" in chuxing:
                pos_insid_list_chuxing += [0,7,16,21,22]
                pos_insid_list_chuxing = list(set(pos_insid_list_chuxing) - set(pos_insid_list_shouru))
                pos_insid = pos_insid_list_chuxing[random.randint(0, len(pos_insid_list_chuxing) - 1)]
                fw.write(f"{_uid}\t{pos_insid}\t1\n")
                _tmp.append(pos_insid)

            pos_insid_list_health = []
            if "很健康" in health or "0" in health:
                pos_insid_list_health = type2ins["年金险"]+type2ins["分红型"]+type2ins["定期寿险"]
                pos_insid_list_health = list(set(pos_insid_list_health) - set(pos_insid_list_shouru))
                pos_insid = pos_insid_list_health[random.randint(0, len(pos_insid_list_health) - 1)]
                fw.write(f"{_uid}\t{pos_insid}\t1\n")
                _tmp.append(pos_insid)

            pos_insid_list_plus = []
            if "中年" in age and shenghuo in ["常喝酒","睡觉晚","运动少","加班多"] and health in ["肠胃不好","颈椎不适","失眠"]:
                pos_insid_list_plus = type2ins["医疗险"]+type2ins["重疾险"]
                pos_insid = pos_insid_list_plus[random.randint(0, len(pos_insid_list_plus) - 1)]
                fw.write(f"{_uid}\t{pos_insid}\t1\n")
                _tmp.append(pos_insid)



            num_ins = len(_tmp)
            if num_ins == 0:
                num_ins = random.randint(0, 4)
                _tmp = []
                _uid = row['UID']
                for _ in range(num_ins):
                    pos_insid = insID_all[random.randint(0, len(insID_all) - 1)]
                    if pos_insid not in _tmp:
                        _tmp.append(pos_insid)
                        fw.write(f"{_uid}\t{pos_insid}\t1\n")

            sub_insid = list(set(insID_all) - set(_tmp))
            _tmp = []
            for _ in range(num_ins*2):
                neg_insid = sub_insid[random.randint(0,len(sub_insid)-1)]
                if neg_insid not in _tmp:
                    _tmp.append(neg_insid)
                    fw.write(f"{_uid}\t{neg_insid}\t0\n")

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
    # user2ins_plus("./users_feats.csv", "./insurance_data.csv", "./click_plus.csv")
    cmobine_userIns("./users_feats.csv", "./insurance_data.csv", "./click_plus.csv", "combine_features_plus.csv")
