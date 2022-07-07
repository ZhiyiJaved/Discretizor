from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


def knn_transform(data, column, k):
    """返回数据和质心"""
    data_copy = data.copy()
    data = MinMaxScaler().fit_transform(data)
    estimator = KMeans(n_clusters=k)
    estimator.fit(data)
    data_copy[f"{column}_category"] = pd.DataFrame(estimator.labels_)
    return data_copy


def kd_range(data):
    record = {}
    temp = None
    for i in range(len(data)):
        if temp is None:
            temp = data[i]
            record[temp] = []
            start = i
        elif temp != data[i]:
            # 结束上一次记录
            end = i - 1
            record[temp].append([start, end])
            # 开始下一次记录
            start = i
            temp = data[i]
            # 若没有记录则添加类别记录
            try:
                record[temp]
            except:
                record[temp] = []
            # 如果是最后一个，则直接加入记录
        elif i == len(data) - 1:
            record[temp].append([start, i])
    return {'name': 'record_discretization', 'value': record}
