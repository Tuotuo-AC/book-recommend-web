import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域，供 Vue 前端调用

# 加载模型
with open('svd_model.pkl', 'rb') as f:
    model = pickle.load(f)

P = model['P']
Q = model['Q']
b_u = model['b_u']
b_i = model['b_i']
global_mean = model['global_mean']
idx_to_title = model['idx_to_title']

n_items = Q.shape[0]

def recommend_svd(user_id, n=10):
    rated = set()   # 空集合表示不过滤已读
    candidates = [i for i in range(n_items) if i not in rated]
    recs = []
    for i in candidates:
        pred = global_mean + b_u[user_id] + b_i[i] + np.dot(P[user_id], Q[i])
        # 将评分裁剪到 [1, 10] 区间（因为原始评分范围是 1~10）
        pred = np.clip(pred, 1, 10)
        recs.append((i, pred))
    recs.sort(key=lambda x: x[1], reverse=True)
    # 按预测分降序排序，取前 n 个
    top_items = recs[:n]
    # 过 idx_to_title 将内部索引转为书名，返回 [(书名, 评分), ...]
    result = [(idx_to_title.get(i, f"未知图书{i}"), score) for i, score in top_items]
    return result

# 定义 /recommend 路由，只接受 POST 方法
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({'error': '缺少 user_id'}), 400
    try:
        user_id = int(user_id)
        if user_id < 0 or user_id >= P.shape[0]:
            return jsonify({'error': f'用户ID范围 0-{P.shape[0]-1}'}), 400
        # 调用 recommend_svd 得到推荐结果，组装成 JSON 返回
        recs = recommend_svd(user_id, n=10)
        return jsonify({'recommendations': [{'title': t, 'score': s} for t, s in recs]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)