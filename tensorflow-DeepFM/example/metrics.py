from sklearn.metrics import roc_auc_score
import numpy as np

def gini(actual, pred):
    assert (len(actual) == len(pred))
    all = np.asarray(np.c_[actual, pred, np.arange(len(actual))], dtype=np.float)
    all = all[np.lexsort((all[:, 2], -1 * all[:, 1]))]
    totalLosses = all[:, 0].sum()
    giniSum = all[:, 0].cumsum().sum() / totalLosses

    giniSum -= (len(actual) + 1) / 2.
    return giniSum / len(actual)

def auc(actual, pred):
    assert (len(actual) == len(pred))
    auc = roc_auc_score(actual, pred)
    return auc

def gini_norm(actual, pred):
    return gini(actual, pred) / gini(actual, actual)
