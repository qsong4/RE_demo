import jieba

class RS_recall(object):
    def __init__(self):
        insurance_data = "./data/insurance_data.csv"
        self.invertIndex = self._build_invertIndex(insurance_data)

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

    def recall(self, content):
        # print(self.invertIndex)
        recall_list = []
        w_list = set(jieba.lcut(content))
        for w in w_list:
            if w in self.invertIndex:
                recall_list.extend(self.invertIndex[w])
            else:
                continue
        return recall_list

if __name__ == '__main__':
    content = "我想要个少儿保险和重疾险"
    rs_recall = RS_recall()
    res = rs_recall.recall(content)
    print(res)







