from flask import Flask, jsonify, request
from flask_cors import CORS
from client.src.data_process.data_time_process.get_data import *
from client.src.data_process.data_time_process.predict_data import *
from client.src.data_process.data_time_process.describe_data import *

# configuration

DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS

CORS(app)


############# 前后端交互的代码 ##############################
@app.route('/describe_feature_data', methods=['GET', 'POST'])
def describe_feature_data():
    data = describe_data()
    json = jsonify(data)
    return json


@app.route('/count_feature_data', methods=['GET', 'POST'])
def count_feature_data():
    try:
        feature = request.json['feature']
    except:
        data = count_data(None, None)
    else:
        try:
            interval = float(request.json['interval'])
        except:
            data = count_data(feature, None)
        else:
            data = count_data(feature, interval)
    json = jsonify(data)
    return json


@app.route('/get_feature_data', methods=['GET', 'POST'])
def get_feature_data():
    feature = request.json['feature']
    try:
        interval = float(request.json['interval'])
    except:
        data = jsonify_ratio(get_data(feature, None, None))
    else:
        data = jsonify_ratio(get_data(feature, interval, deepth=None))
    json = jsonify(data)
    return json


@app.route('/sg_feature_data', methods=['GET', 'POST'])
def sg_feature_data():
    feature = request.json['feature']
    window = int(request.json['window'])
    rank = int(request.json['rank'])
    try:
        interval = int(request.json['interval'])
    except:
        data_bd = get_data(feature, None, None)
        data_sg, json_sg_derivative, json_scatter, json_record_kd = sg_data(data_bd, window, rank)  # sg_data函数返回四个值
        data = jsonify_ratio(data_bd, data_sg, 'sg')
        data.append(json_sg_derivative)
        data.append(json_scatter)
        data.append(json_record_kd)
    else:
        data_bd = get_data(feature, interval, None)
        data_sg, json_sg_derivative, json_scatter, json_record_kd = sg_data(data_bd, window, rank)  # sg_data函数返回四个值
        data = jsonify_ratio(data_bd, data_sg, 'sg')
        data.append(json_sg_derivative)
        data.append(json_scatter)
        data.append(json_record_kd)
    json = jsonify(data)
    return json


@app.route('/cluster_feature_data', methods=['GET', 'POST'])
def cluster_feature_data():
    feature = request.json['feature']
    window = int(request.json['window'])
    rank = int(request.json['rank'])
    clusters = int(request.json['clusters'])
    try:
        interval = int(request.json['interval'])
    except:
        data_bd = get_data(feature, None, None)
        data_sg, json_scatter, json_record_kd = sg_data(data_bd, window, rank, clusters)  # sg_data函数返回四个值
        data = jsonify_ratio(data_bd, data_sg, 'sg')
        data.append(json_scatter)
        data.append(json_record_kd)
    else:
        data_bd = get_data(feature, interval, None)
        data_sg, json_scatter, json_record_kd = sg_data(data_bd, window, rank, clusters)  # sg_data函数返回四个值
        data = jsonify_ratio(data_bd, data_sg, 'sg')
        data.append(json_scatter)
        data.append(json_record_kd)
    json = jsonify(data)
    return json


@app.route('/td_feature_data', methods=['GET', 'POST'])
def td_feature_data():
    feature = request.json['feature']
    deepth = int(request.json['deepth'])
    try:
        interval = int(request.json['interval'])
    except:
        data_bd = get_data(feature, None, None)
        data_td = get_data(feature, None, deepth)
        data = jsonify_ratio(data_bd, data_td, 'td_spe')
        data.append(td_range(data_td.tolist()))  # 带入范围信息
    else:
        data_bd = get_data(feature, interval, None)
        data_td = get_data(feature, interval, deepth)
        data = jsonify_ratio(data_bd, data_td, 'td_spe')
        data.append(td_range(data_td.tolist()))  # 带入范围信息
    json = jsonify(data)
    return json


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    feature_composition = request.json['feature_composition']
    result = request.json['result']
    interval = request.json['interval']
    data_pre = predict_data(feature_composition, result, interval)
    json = jsonify(data_pre)
    return json


if __name__ == '__main__':
    app.run()
