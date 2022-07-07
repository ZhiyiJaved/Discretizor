import pandas as pd

df = pd.read_csv(u"/Users/duiba/PycharmProjects/flask_test/static/train_test.csv")  # 全体数据
df = df[df >= 0].dropna()
df = df.reset_index().drop('index', axis=1)  # 重置标号


def describe_data():
    data_interval_range = {}
    data_information = {}
    features = df.columns[1:13].tolist()
    for i in features:
        temp = df[i]
        max = temp.max()
        min = temp.min()
        data_information[i] = {'max': max, 'min': min}
        data_interval_range[i] = {'maxInterval': max / 10, 'minInterval': max / 500}
    return {'features': features, 'describe': data_information, 'intervalRange': data_interval_range}


def count_temp(feature, n, json):
    temp = pd.DataFrame(df[feature].copy())
    if n is None:
        n_min = temp[feature].max() / 500
        n_max = temp[feature].max() / 10
        n = (n_min + n_max) / 2
    temp[f"label_{feature}"] = temp[feature] // n
    count = temp.groupby(f"label_{feature}").size()
    json[f'{feature}'] = [{'x': i, 'y': j} for i, j in zip(count.index, count)]
    return json


def count_data(feature, interval):
    json = {}
    if feature is None:
        features = df.columns[1:13].tolist()
        for i in features:
            count_temp(i, interval, json)
    elif interval is None:
        count_temp(feature, interval, json)
    else:
        count_temp(feature, interval, json)
    return json
