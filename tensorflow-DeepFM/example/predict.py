import os
import sys
cur_dir = os.path.dirname(__file__)
sys.path.append(cur_dir)
import numpy as np
import pandas as pd
import tensorflow as tf
import pickle
import config_pred as config
from metrics import auc
from DataReader import FeatureDictionary, DataParser
from DeepFM import DeepFM
import time

dfm_params = {
    "use_fm": True,
    "use_deep": True,
    "embedding_size": 8,
    "dropout_fm": [1.0, 1.0],
    "deep_layers": [32, 32],
    "dropout_deep": [0.5, 0.5, 0.5],
    "deep_layers_activation": tf.nn.relu,
    "epoch": 5,
    "batch_size": 1,
    "learning_rate": 0.001,
    "optimizer_type": "adam",
    "batch_norm": 1,
    "batch_norm_decay": 0.995,
    "l2_reg": 0.01,
    "verbose": True,
    "eval_metric": auc,
    "random_seed": config.RANDOM_SEED,
    "model_path": config.MODEL_PATH,
}
class dfm_predict(object):
    def __init__(self):
        with open(cur_dir + config.DF_FILE, 'rb') as fd_f:
            fd = pickle.load(fd_f)
        dfm_params["feature_size"] = fd.feat_dim
        dfm_params["field_size"] = 18
        self.userfeats, self.insfeats = self._load_dict()

        self.data_parser = DataParser(feat_dict=fd)
        self.dfm = DeepFM(**dfm_params)
        self.dfm.load_model(cur_dir + config.MODEL_DIR)
        # print(fd["1"])

    def _load_dict(self):
        userfeats = pd.read_csv(cur_dir + config.USER_FILE, sep="\t", header=0)
        insfeats = pd.read_csv(cur_dir + config.INS_FILE, sep="\t", header=0)
        return userfeats, insfeats

    def predict(self,users_feats, ins_feats):
        users_feats.update(ins_feats)
        # print(users_feats)
        dfTest = pd.DataFrame([users_feats])

        Xi_test, Xv_test, y_test = self.data_parser.parse(df=dfTest, has_label=False)  # 测试集也是有label

        res = self.dfm.predict(Xi_test, Xv_test)
        return res

    def predict_plus(self,uID, insID):
        ins_feats = self.insfeats.loc[self.insfeats['InsID'].isin([insID])]
        users_feats = self.userfeats.loc[self.userfeats['UID'].isin([uID])]
        #若用户不存在,直接返回相似度为1
        if users_feats.empty:
            return [1]
        #若保险不存在，返回相似度为0
        if ins_feats.empty:
            return [0]
        # print("ins_feats:")
        # print(ins_feats)
        # print("users_feats:")
        # print(users_feats)
        ins_feats['tmp'] = 1
        users_feats['tmp'] = 1

        dfTest = pd.merge(users_feats, ins_feats, on=['tmp'])

        dfTest = dfTest.drop("tmp",axis=1)

        Xi_test, Xv_test, y_test = self.data_parser.parse(df=dfTest, has_label=False)  # 测试集也是有label
        try:
            res = self.dfm.predict(Xi_test, Xv_test)
        except:
            print(f"数据中有nan:{Xi_test}")
            return [0]
        return res

    def predict_plus_plus(self, uID, insIDs):
        ins_feats = []
        users_feats = []
        for insID in insIDs:
            ins_feat = self.insfeats.loc[self.insfeats['InsID'].isin([insID])]
            users_feat = self.userfeats.loc[self.userfeats['UID'].isin([uID])]
            ins_feats.append(ins_feat)
            users_feats.append(users_feat)
            # print(ins_feats)
        ins_feats = pd.concat(ins_feats)
        users_feats = pd.concat(users_feats)
        #若用户不存在,直接返回相似度为1
        if users_feats.empty:
            return [1]
        #若保险不存在，返回相似度为0
        if ins_feats.empty:
            return [0]
        ins_feats.index = range(len(ins_feats))
        users_feats.index = range(len(users_feats))

        dfTest = pd.concat([users_feats, ins_feats], axis=1)

        Xi_test, Xv_test, y_test = self.data_parser.parse(df=dfTest, has_label=False)  # 测试集也是有label
        try:
            res = self.dfm.predict(Xi_test, Xv_test)
        except:
            print(f"数据中有nan:{Xi_test}")
            return [0]
        return res


if __name__ == '__main__':
    pre = dfm_predict()
    users_feats={"ID":"0","UID":"1","性别":"女","年龄":"幼儿","收入":"高","职业":"高危职业","出行方式":"电动车","生活习惯":"0","健康情况":"0",
                 "是否贷款":"否","已购保险类型":"意外险"}
    ins_feats = {"InsID":12,"保险名":"平安手机碎屏险（苹果版）","类型":"意外险","价格":"高","适合年龄":"幼儿|青年|中年|老年",
                 "保单形式":"电子|纸质","销售范围":"大陆","适用疾病":"0","适用职业":"0","缴费方式":"年缴|月缴|一次性","关键词":""}
    # res = pre.predict(users_feats, ins_feats)
    # start = time.time()
    # res = pre.predict_plus("2", "14")
    # end = time.time()
    # print(end-start)
    # print(res)
    # start = time.time()
    # res = pre.predict_plus("2", "14")
    # end = time.time()
    # print(end-start)
    # print(res)
    start = time.time()
    res = pre.predict_plus_plus("2", ["14","14","14"])
    end = time.time()
    print(end-start)
    print(res)



