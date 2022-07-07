from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd


def td_range(data):
    record = {}
    temp = None
    flag = 0
    dict_flag = {}
    for i in range(len(data)):
        if temp is None:
            temp = data[i]  # 保存当前元素位置
            dict_flag[temp] = flag  # 保存当前元素的对应关系
            record[dict_flag[temp]] = []  # 用当前元素对应的旗子作字典的键
            start = i  # 当前元素位置作为开始位置
        elif abs(temp - data[i]) > 0.000001:  # 由于未知原因，存在小数点后数据误差
            # 结束上一次记录
            end = i - 1
            record[dict_flag[temp]].append([start, end])  # 通过dict_flag的对应关系找到应该添加的记录表
            # 开始下一次记录
            start = i
            temp = data[i]
            # 若没有记录则添加类别记录
            try:
                record[dict_flag[temp]]
            except:
                flag += 1  # 旗子递增1
                dict_flag[temp] = flag  # 动态添加对应关系
                record[dict_flag[temp]] = []  # 添加新纪录
            # 如果是最后一个，则直接加入记录
        elif i == len(data) - 1:
            record[dict_flag[temp]].append([start, i])
    return {'name': 'record_discretization', 'value': record}


class tree_discretize():

    def __init__(self, data, features, labels, n=6):
        """data是有着所有需要离散变量数据的矩阵，features是一个需要离散的变量名列表，labels则是一列决策树标签值，n为决策深度"""
        self.data = data
        self.features = features
        self.labels = labels
        self.n = n

    def discretize_tree(self, best_deepth):
        """best_deepth是一个字典，定义了每个特征的最佳离散深度"""
        df = pd.DataFrame()
        features_discretized = []
        best_discretize_tree = {}
        for i, j in best_deepth.items():
            df_feature = self.data[i].to_frame()
            tree_model = DecisionTreeClassifier(max_depth=j)  # 按照字典要求的最佳深度创建模型
            tree_model.fit(df_feature, self.labels)  # 将输入数据转化为可以拟合的数据类型
            best_discretize_tree[i] = tree_model  # 每个特征对应一棵训练好的决策树
            df[i + "_tree"] = tree_model.predict_proba(df_feature)[:, 1]  # 以阳性概率作为离散特征值
            features_discretized.append(i + "_tree")  # 将被离散化的特征名加入
        return features_discretized, df, best_discretize_tree

    def best_discretize_tree(self):
        """获取最佳离散深度并将变量传递到discretize_tree（）"""
        best_deepth = {}
        for feature in self.features:
            score_ls = []  # here I will store the roc auc
            score_std_ls = []  # here I will store the standard deviation of the roc_auc
            for tree_depth in range(2, self.n + 1):
                tree_model = DecisionTreeClassifier(max_depth=tree_depth)

                scores = cross_val_score(tree_model, self.data[feature].to_frame(),
                                         self.labels, cv=5, scoring='roc_auc')
                score_ls.append(np.mean(scores))
                score_std_ls.append(np.std(scores))
            temp = pd.concat([pd.Series(np.arange(2, self.n + 1)), pd.Series(
                score_ls), pd.Series(score_std_ls)], axis=1)
            temp.columns = ['depth', 'roc_auc_mean', 'roc_auc_std']
            temp = temp.sort_values(by="roc_auc_mean", ascending=False)
            number = int(temp.iloc[0]["depth"])
            print(f"特征{feature}离散化的最佳决策深度为{number}")
            best_deepth[feature] = number
        return self.discretize_tree(best_deepth)
