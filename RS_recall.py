import jieba
import numpy as np
import math
from tqdm import tqdm

class RS_recall(object):
    def __init__(self):
        insurance_data = "./data/insurance_data.csv"
        w2v_data = "./data/w2v.txt"
        self.invertIndex = self._build_invertIndex(insurance_data)
        self.w2v = self._build_w2vec(w2v_data)
        self.ins2v = self._build_ins2vec(insurance_data)
        # print(self.w2v)
        # print(self.ins2v)

    def _build_w2vec(self, w2v_data):
        embed = {}
        with open(w2v_data, 'r') as fr:
            for line in tqdm(fr):
                row = line.rstrip().split(' ')
                if row[0] in embed.keys():
                    continue
                else:
                    assert len(row[1:]) == 200
                    embed[row[0]] = np.array([float(v) for v in row[1:]])
        return embed

    def _build_ins2vec(self, infile):
        ins2vec = {}
        with open(infile, "r") as fr:
            next(fr)  # 过滤表头
            for line in fr:
                content = line.strip().split('\t')
                ins_name = content[0]
                if ins_name in ins2vec:
                    continue
                else:
                    key_words = content[-1].split('|')
                    tmp = np.array([0.0]*200)
                    count = 0
                    for k in key_words:
                        if k in self.w2v:
                            count+=1
                            tmp += self.w2v[k]
                        else:
                            continue
                    if count != 0:
                        tmp = tmp/count
                    ins2vec[ins_name] = tmp
        return ins2vec

    def _build_invertIndex(self, infile):
        _ins2feat = {}
        all_words = []
        with open(infile, "r") as fr:
            next(fr)#过滤表头
            for line in fr:
                content = line.strip().split('\t')
                ins_name = content[0]
                if ins_name not in _ins2feat:
                    _ins2feat[ins_name] = content[-1]
                else:
                    continue
                key_words = content[-1].split('|')
                all_words.extend(key_words)
        set_words = set(all_words)

        inverIndex = {}
        for w in set_words:
            #jieba加入自定义词典
            jieba.add_word(w)
            _n = []
            for k, v in _ins2feat.items():
                if w in v:
                    _n.append(k)
            if w not in inverIndex:
                inverIndex[w] = _n
            else:
                print("这不可能")
                continue
        # print(inverIndex)
        return inverIndex

    def cosSimi(self, v1, v2):
        vec1 = np.array(v1, dtype=float)
        vec2 = np.array(v2, dtype=float)
        tmp = np.vdot(vec1, vec1) * np.vdot(vec2, vec2)
        # print(tmp)
        if tmp == 0.0:
            return 0.0
        return np.dot(vec1, vec2)/math.sqrt(tmp)

    def contentVec(self, content):
        wl = jieba.lcut(content)
        # print(wl)
        tmp = np.array([0.0]*200)
        count = 0
        for w in wl:
            if w in self.w2v:
                count+=1
                tmp+=self.w2v[w]
        if count == 0:
            return tmp
        return tmp/count

    def vecRecall(self, content, topk=5):
        #key保险编号value相似度得分
        ins_res = {}
        contentvec = self.contentVec(content)
        for k, v in self.ins2v.items():
            score = self.cosSimi(contentvec, v)
            ins_res[k] = score
        res = sorted(ins_res.items(), key=lambda item:item[1], reverse=True)
        return res[:topk]

    def recall(self, content, topk=5):
        # print(self.invertIndex)
        recall_list = []
        w_list = set(jieba.lcut(content))
        for w in w_list:
            if w in self.invertIndex:
                recall_list.extend(self.invertIndex[w])
            else:
                continue
        recall_list = [(ins, 1) for ins in recall_list]
        return recall_list[:topk]

if __name__ == '__main__':
    content = "有没有适合的"
    rs_recall = RS_recall()
    # res = rs_recall.recall(content)
    res = rs_recall.vecRecall(content)
    print(res)







