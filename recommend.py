import os, sys
# cur_dir = os.path.dirname(__file__)
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir + "/tensorflow-DeepFM/example/")
from predict import dfm_predict
from RS_recall import RS_recall
import re
import json
import numpy as np

class Recommend(object):
    def __init__(self):
        self.deepfm_pre = dfm_predict()
        self.rs_recall = RS_recall()
        insurance_data = cur_dir + "/data/insurance_data.csv"
        user_data = cur_dir + "/data/users_feats.csv"
        self.id2name = self._build_id2name(insurance_data)
        # print(self.id2name)
        self.userid_list = self._build_userid(user_data)

    def _build_userid(self, infile):
        ids = []
        with open(infile, "r") as fr:
            next(fr)#过滤表头
            for line in fr:
                content = line.strip().split('\t')
                u_id = content[0]
                ids.append(ids)
        return ids

    def _build_id2name(self, infile):
        id2name = {}
        with open(infile, "r") as fr:
            next(fr)#过滤表头
            for line in fr:
                content = line.strip().split('\t')
                ins_id = content[0]
                ins_name = content[1]
                id2name[ins_id] = ins_name
        return id2name

    def deepfm_result(self, uid, insids):
        """
        :param uid: 用户ID
        :param insids: 保险ID [x,y,z]
        :return: [(insid,score),()]有序的
        """
        result = {}
        for insid in insids:
            #返回值为list
            # print(uid)
            # print(insid)
            score = self.deepfm_pre.predict_plus(uid, insid)[0]
            result[insid] = score
        result = sorted(result.items(), key=lambda x:x[1], reverse=True)
        return result

    def kw_recall(self, content):
        """
        关键词倒排索引召回
        :param content: 用户当前会话内容
        :return:
        """
        res = self.rs_recall.recall(content)
        return res

    def vec_recall(self, content):
        """
        向量相似度召回
        :param content: 用户当前会话内容
        :return:
        """
        res = self.rs_recall.vecRecall(content)
        return res

    def main_handle(self, uid, content, tag=None):
        """
        :param uid: 用户ID,unk时为冷启动状态，没有用户历史信息
        :param content: 用户当前轮聊天内容
        :param tag: 标签位，暂时没用以备不时之需
        :return:
        """
        # 使用基于关键词的召回
        recall_res = self.kw_recall(content)
        # 关键词无法召回，使用基于向量的召回
        # if len(recall_res) == 0:
            # 召回不到也会默认返回5个
            # recall_res = self.vec_recall(content)
        print("召回结果：")
        print(recall_res)
        #冷启动状态，使用基于内容的召回
        if uid == "unk" and uid not in self.userid_list:
            print("冷启动.....")
            if len(recall_res) == 0:
                recall_res = self.vec_recall(content, 5)
            return [(self.id2name[id], score) for id,score in recall_res]
        else:
            print("DeepFM Rank....")
            #如果前面召回失败，则用所有保险去计算
            if len(recall_res) == 0 or recall_res[0][1]==0.0:
                recall_res = self.id2name.keys()
                rank_res = self.deepfm_result(uid, recall_res)
            else:
                recall_res = [id for id,_ in recall_res]
                rank_res = self.deepfm_result(uid, recall_res)
            return [(self.id2name[id], score) for id,score in rank_res]

if __name__ == '__main__':
    content = "保险推荐"
    rs = Recommend()
    res = rs.main_handle(uid="1", content=content)
    print(res)



