
import os
import sys

import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.metrics import make_scorer
from sklearn.model_selection import StratifiedKFold
import pickle
import config
from metrics import auc
from DataReader import FeatureDictionary, DataParser
# sys.path.append("..")
from DeepFM import DeepFM

# gini_scorer = make_scorer(gini_norm, greater_is_better=True, needs_proba=True)
# auc_scorer = make_scorer(auc, greater_is_better=True, needs_proba=True)

def _load_data():

    dfTrain = pd.read_csv(config.TRAIN_FILE)
    dfTest = pd.read_csv(config.TEST_FILE)

    def preprocess(df):
        # cols = [c for c in df.columns if c not in ["id", "target"]]
        # df["missing_feat"] = np.sum((df[cols] == -1).values, axis=1)
        # df["ps_car_13_x_ps_reg_03"] = df["ps_car_13"] * df["ps_reg_03"]
        return df

    dfTrain = preprocess(dfTrain)
    dfTest = preprocess(dfTest)

    cols = [c for c in dfTrain.columns if c not in ["InsID", "ID", "target"]]
    cols = [c for c in cols if (not c in config.IGNORE_COLS)]

    X_train = dfTrain[cols].values
    y_train = dfTrain["target"].values
    X_test = dfTest[cols].values
    # ids_test = dfTest["id"].values
    y_test = dfTest["target"].values
    cat_features_indices = [i for i,c in enumerate(cols) if c in config.CATEGORICAL_COLS]

    return dfTrain, dfTest, X_train, y_train, X_test, y_test, cat_features_indices


def _run_base_model_dfm(dfTrain, dfTest, folds, dfm_params):
    if os.path.exists(config.DF_FILE):
        print("FD EXISTED")
        with open(config.DF_FILE, 'rb') as fd_f:
            fd = pickle.load(fd_f)
    else:
        print("FD NO EXISTED")
        fd = FeatureDictionary(dfTrain=dfTrain, dfTest=dfTest,
                               numeric_cols=config.NUMERIC_COLS,
                               ignore_cols=config.IGNORE_COLS)
        with open(config.DF_FILE, 'wb') as fd_f:
            pickle.dump(fd, fd_f)

    data_parser = DataParser(feat_dict=fd)
    Xi_train, Xv_train, y_train = data_parser.parse(df=dfTrain, has_label=True)
    Xi_test, Xv_test, y_test = data_parser.parse(df=dfTest, has_label=True) #测试集也是有label
    # print(y_test)
    # print(Xi_train)
    # print(Xv_train)
    # print(y_train)

    dfm_params["feature_size"] = fd.feat_dim
    dfm_params["field_size"] = len(Xi_train[0])
    print(dfm_params)
    # print(dfm_params)

    y_train_meta = np.zeros((dfTrain.shape[0], 1), dtype=float)
    y_test_meta = np.zeros((dfTest.shape[0], 1), dtype=float)
    _get = lambda x, l: [x[i] for i in l]
    auc_results_cv = np.zeros(len(folds), dtype=float)
    test_auc_results_cv = np.zeros(len(folds), dtype=float)
    auc_results_epoch_train = np.zeros((len(folds), dfm_params["epoch"]), dtype=float)
    auc_results_epoch_valid = np.zeros((len(folds), dfm_params["epoch"]), dtype=float)
    # best_test_res = 0.0
    for i, (train_idx, valid_idx) in enumerate(folds):
        print(f"Fold {i}:")
        Xi_train_, Xv_train_, y_train_ = _get(Xi_train, train_idx), _get(Xv_train, train_idx), _get(y_train, train_idx)
        Xi_valid_, Xv_valid_, y_valid_ = _get(Xi_train, valid_idx), _get(Xv_train, valid_idx), _get(y_train, valid_idx)
        # print(Xi_train_)
        # print(Xv_train_)
        # print(y_train_)
        # print(Xi_valid_)
        # print(Xv_valid_)
        # print(y_valid_)
        dfm = DeepFM(**dfm_params)
        dfm.fit(Xi_train_, Xv_train_, y_train_, Xi_valid_, Xv_valid_, y_valid_, i)

        y_train_meta[valid_idx,0] = dfm.predict(Xi_valid_, Xv_valid_)
        y_test_meta[:,0] = dfm.predict(Xi_test, Xv_test)
        auc_results_cv[i] = auc(y_valid_, y_train_meta[valid_idx])
        test_auc_results = auc(y_test, y_test_meta)
        # if test_auc_results > best_test_res:
        #     MODEL_PATH = config.MODEL_PATH % (i, )
        #     dfm.save_model(config.MODEL_PATH)#可以写保存地址

        test_auc_results_cv[i] = test_auc_results
        auc_results_epoch_train[i] = dfm.train_result
        auc_results_epoch_valid[i] = dfm.valid_result

    y_test_meta /= float(len(folds))

    # save result
    if dfm_params["use_fm"] and dfm_params["use_deep"]:
        clf_str = "DeepFM"
    elif dfm_params["use_fm"]:
        clf_str = "FM"
    elif dfm_params["use_deep"]:
        clf_str = "DNN"
    print("%s: %.5f (%.5f)"%(clf_str, auc_results_cv.mean(), auc_results_cv.std()))
    print("test auc: ", test_auc_results_cv)
    filename = "%s_Mean%.5f_Std%.5f.csv"%(clf_str, auc_results_cv.mean(), auc_results_cv.std())
    # _make_submission(ids_test, y_test_meta, filename)

    # _plot_fig(auc_results_epoch_train, auc_results_epoch_valid, clf_str)

    return y_train_meta, y_test_meta


def _make_submission(ids, y_pred, filename="submission.csv"):
    pd.DataFrame({"id": ids, "target": y_pred.flatten()}).to_csv(
        os.path.join(config.SUB_DIR, filename), index=False, float_format="%.5f")


def _plot_fig(train_results, valid_results, model_name):
    colors = ["red", "blue", "green"]
    xs = np.arange(1, train_results.shape[1]+1)
    plt.figure()
    legends = []
    for i in range(train_results.shape[0]):
        plt.plot(xs, train_results[i], color=colors[i], linestyle="solid", marker="o")
        plt.plot(xs, valid_results[i], color=colors[i], linestyle="dashed", marker="o")
        legends.append("train-%d"%(i+1))
        legends.append("valid-%d"%(i+1))
    plt.xlabel("Epoch")
    plt.ylabel("Normalized auc")
    plt.title("%s"%model_name)
    plt.legend(legends)
    plt.savefig("./fig/%s.png"%model_name)
    plt.close()

print("LOADING DATA........")
# load data
dfTrain, dfTest, X_train, y_train, X_test, y_test, cat_features_indices = _load_data()
# print(dfTrain)
# print("****************")
# print(dfTest)
# print("****************")
# print(X_train)
# print("****************")
# print(y_train)
# print("****************")
# print(X_test)
# print("****************")
# print(y_test)
# print("****************")
# print(cat_features_indices)


# folds
print("Build K-Fold...........")
folds = list(StratifiedKFold(n_splits=config.NUM_SPLITS, shuffle=True,
                             random_state=config.RANDOM_SEED).split(X_train, y_train))


# ------------------ DeepFM Model ------------------
# params
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
print("START Training...........")
y_train_dfm, y_test_dfm = _run_base_model_dfm(dfTrain, dfTest, folds, dfm_params)

# # ------------------ FM Model ------------------
# fm_params = dfm_params.copy()
# fm_params["use_deep"] = False
# y_train_fm, y_test_fm = _run_base_model_dfm(dfTrain, dfTest, folds, fm_params)
#
#
# # ------------------ DNN Model ------------------
# dnn_params = dfm_params.copy()
# dnn_params["use_fm"] = False
# y_train_dnn, y_test_dnn = _run_base_model_dfm(dfTrain, dfTest, folds, dnn_params)



