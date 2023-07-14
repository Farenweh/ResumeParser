import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from sklearn.cluster import DBSCAN

from config.Config import layout_threshold

with open('108.json', 'r') as f:
    a = json.load(f)
    b = []
    for each in a:
        b.append({'word': each['word'],
                  'position': each['position']})
rects = []
for each in b:
    rects.append(each['position'])
print(b)


def draw_rectangle(rect):
    x = [p['x'] for p in rect]
    y = [p['y'] for p in rect]
    plt.plot(x + [x[0]], y + [y[0]], color='red')


# 绘制所有矩形
for rect in rects:
    draw_rectangle(rect)

# 设置坐标轴范围
plt.xlim(0, 5000)
plt.ylim(0, 5000)
ax = plt.gca()
ax.invert_yaxis()  # y轴反向

# 显示图像
# plt.show()


# 将每个矩形表示为一个点
# 数据格式为：[[{'x': x1, 'y': y1}, {'x': x2, 'y': y2}, {'x': x3, 'y': y3}, {'x': x4, 'y': y4}], ...]

# 数据转换为NumPy数组
data = np.array(rects)


# 计算矩形之间的距离
def distance(rect1, rect2):
    x1 = [p['x'] for p in rect1]
    y1 = [p['y'] for p in rect1]
    x2 = [p['x'] for p in rect2]
    y2 = [p['y'] for p in rect2]
    dx = np.max([np.min(x2) - np.max(x1), 0, np.min(x1) - np.max(x2), 0])
    dy = np.max([np.min(y2) - np.max(y1), 0, np.min(y1) - np.max(y2), 0])
    return np.sqrt(dx * dx + dy * dy)


# 计算矩形之间的距离矩阵
dist_matrix = np.zeros((len(data), len(data)))
for i in range(len(data)):
    for j in range(len(data)):
        if i == j:
            dist_matrix[i, j] = 0
        else:
            dist_matrix[i, j] = distance(data[i], data[j])

# 使用DBSCAN进行聚类
dbscan = DBSCAN(eps=layout_threshold, min_samples=1, metric='precomputed')
labels = dbscan.fit_predict(dist_matrix)

# 打印聚类结果
print(labels)
fig, ax = plt.subplots()

colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', '#FFA500', '#800080', '#008080', '#FFC0CB', '#800000', '#FF00FF',
          '#00FFFF', '#FF69B4', '#FFFF00', '#008000', '#FF7F50', '#800080', '#FF4500']

for i in range(len(data)):
    polygon = Polygon([(p['x'], p['y']) for p in data[i]], fill=None, edgecolor=colors[labels[i]])
    ax.add_patch(polygon)

ax.set_xlim([0, 5000])
ax.set_ylim([0, 5000])
ax.set_aspect('equal')
ax.invert_yaxis()
plt.show()
