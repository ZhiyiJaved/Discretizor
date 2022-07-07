from client.src.data_process.data_time_process.tree_discretize import *
from client.src.data_process.data_time_process.kmeans_discretize import *
from scipy.signal import savgol_filter

df = pd.read_csv(u"/Users/duiba/PycharmProjects/flask_test/static/train_test.csv")  # 全体数据
df = df[df >= 0].dropna()
df = df.reset_index().drop('index', axis=1)  # 重置标号


# 基础数据获取与数据拟合
def get_data(feature, n, deepth):
    data = df[[feature, 'isDefault']].copy()  # 提取需要特征
    if n is None:
        n_min = data[feature].max() / 500
        n_max = data[feature].max() / 10
        n = (n_min + n_max) / 2
    data[f"label_{feature}"] = data[feature] // n  # 以n为间隔进行区间分块
    condition = data.groupby(f"label_{feature}").size() >= 0  # 样本基数需要大于30
    label_condition = condition[condition == True].index.tolist()  # 大于30个样本的样本标签
    # 如果存在deepth参数，则提供预测数据
    if deepth is not None:
        data = data[data[f"label_{feature}"].isin(label_condition)]  # 统一连接序号
        data.reset_index(inplace=True)
        data.drop("index", axis=1, inplace=True)

        td_spe = tree_discretize(data, [
            f"label_{feature}"], data.isDefault).discretize_tree({f"label_{feature}": deepth})  # 专家离散层数
        td_spe[1].columns = ["td_spe"]  # 将训练的离散特征概率值加入原数据
        data_td_spe = pd.concat([data, td_spe[1]], axis=1)
        ratio_td_spe = data_td_spe.groupby(f"label_{feature}").td_spe.mean()  # 获取每个标签对应的概率值
        data = ratio_td_spe.copy()
    # 否则只是获取基础折线图的数据
    else:
        count = data.groupby(f"label_{feature}").size().rename("count_")  # 各区间的样本数量
        count_positive = data[df.isDefault == 1].groupby(f"label_{feature}").size().rename(
            "count_positive")  # 各区间阳性样本数量
        temp = pd.concat([count, count_positive], axis=1).fillna(0)[condition]  # 连接并补充样本数量条件
        ratio = temp.count_positive / temp.count_  # 计算各区间阳性率
        data = ratio.copy()
    return data


def sg_data(ratio, window, rank, clusters=None):
    # 做sg平滑
    ratio_sg = savgol_filter(ratio, window, rank)
    range_sg = range(len(ratio_sg) - 1)
    # 求增长
    ratio_sg_derivative = [ratio_sg[i + 1] - ratio_sg[i] for i in range_sg]
    # 求类别
    data_kmeans = pd.concat(
        (pd.Series(ratio_sg).rename('ratio_sg'), pd.Series(ratio_sg_derivative).rename('ratio_sg_derivative')),
        axis=1)  # 转化数据类型并连接
    data_kmeans.dropna(inplace=True)
    # 正常流程都得做
    if clusters is None:
        clusters = 3
        data_kd = knn_transform(data_kmeans, 'sg_observe', clusters)
        json_record_kd = kd_range(data_kd.iloc[:, 2].tolist())
        json_derivative = {'name': 'line_derivative',
                           'value': [{'x': i, 'y': j} for i, j in zip(range_sg, ratio_sg_derivative)]}
        json_scatter = {'name': 'scatter',
                        'value': [{'y': ratio_sg[i], 'x': j, 'z': float(data_kd.iloc[i, 2])} for i, j in
                                  zip(range_sg, ratio_sg_derivative)]}  # 转化为浮点就不会报错，很奇怪
        return ratio_sg, json_derivative, json_scatter, json_record_kd
    else:
        data_kd = knn_transform(data_kmeans, 'sg_observe', clusters)
        json_record_kd = kd_range(data_kd.iloc[:, 2].tolist())
        json_scatter = {'name': 'scatter',
                        'value': [{'y': ratio_sg[i], 'x': j, 'z': float(data_kd.iloc[i, 2])} for i, j in
                                  zip(range_sg, ratio_sg_derivative)]}  # 转化为浮点就不会报错，很奇怪
        return ratio_sg, json_scatter, json_record_kd


def jsonify_ratio(ratio, ratio_processed=None, name=None):
    json_line = {'name': 'line',
                 'value': [{'x': i, 'y': j} for i, j in zip(ratio.index, ratio)]}  # 初始折线数据json化
    try:
        json_processed = {'name': f'line_{name}',
                          'value': [{'x': i, 'y': j} for i, j in zip(ratio.index, ratio_processed)]}
        data = [json_line, json_processed]
    except:
        data = [json_line, json_line]
    return data
