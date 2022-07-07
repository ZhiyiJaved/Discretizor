import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, roc_auc_score, log_loss

df = pd.read_csv(u"/Users/duiba/PycharmProjects/flask_test/static/train_test.csv")  # 全体数据
df = df[df >= 0].dropna()  # 去掉小于0的值
df = df.reset_index().drop('index', axis=1)  # 重置标号


def predict_data(feature_composition, result, interval):
    # 离散化数据集
    X = df[feature_composition].copy()
    y = df['isDefault']
    feature_undiscretized = []
    for index_feature, feature in enumerate(feature_composition):  # 编号位置
        if result[index_feature] is not None:
            # 变为折线图区块
            X[feature] = X[feature] // int(interval[index_feature])
            # 计算折线到编码的对映关系
            dict_area = {}
            for area_code, interval_index in enumerate(X[feature].value_counts().sort_index().keys()):
                dict_area[interval_index] = area_code
            # 转化为区域编码
            X[feature] = X[feature].map(dict_area)
            # 生成新的独热编码数据
            for code, area in result[index_feature].items():
                X.eval(f'{feature}_{code} = ({feature} >= {area[0]} & {feature} < {area[1]})', inplace=True)
                # 真假转换为1，0
                X[f'{feature}_{code}'] = X[f'{feature}_{code}'].map(lambda x: 1 if x is True else 0)
            # # 删除原有数据
            X.drop(f"{feature}", axis=1, inplace=True)
        else:
            # 记录未离散的相关特征
            feature_undiscretized.append(feature)
    # 标准化相关数据
    std = StandardScaler()
    if feature_undiscretized:
        X[feature_undiscretized] = std.fit_transform(X[feature_undiscretized])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    lg = LogisticRegression(max_iter=1000)
    lg.fit(X_train, y_train)
    feature_importance = {lg.feature_names_in_[i]: lg.coef_[0][i] for i in range(lg.n_features_in_)}
    # 计算相关指标
    precision = precision_score(y_test, lg.predict(X_test))
    recall = recall_score(y_test, lg.predict(X_test))
    accuracy = accuracy_score(y_test, lg.predict(X_test))
    f1 = f1_score(y_test, lg.predict(X_test))
    # auc = roc_auc_score(y_test, lg.predict(X_test))
    ne = log_loss(y_test, lg.predict(X_test), normalize=True)

    json_metric = {'metrix': {'precision': precision, 'recall': recall, 'accuracy': accuracy, 'f1': f1, 'ne': ne}}
    json_importance = {'feature_importance': feature_importance}
    # json_loss = {'loss': {'ne': ne}}
    return [json_metric, json_importance]
