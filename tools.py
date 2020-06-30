import random
def generw2v(infile, outfile):
    all_words = []
    with open(infile, "r") as fr:
        next(fr)  # 过滤表头
        for line in fr:
            content = line.strip().split('\t')
            key_words = content[-1].split('|')
            all_words.extend(key_words)
    all_words = list(set(all_words))

    with open(outfile, 'w') as fw:
        for w in all_words:
            res = []
            res.append(w)
            for i in range(200):
                res.append(str(random.uniform(-1, 1)))
            fw.write(" ".join(res)+"\n")

generw2v("./data/insurance_data.csv", "./data/w2v.txt")

