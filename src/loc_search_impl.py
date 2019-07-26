import numpy as np
import csv
from timeit import default_timer as timer
import sqlite3
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def find_locations(euler):
    x = int(euler[0])
    y = int(euler[1])
    z = int(euler[2])
    cursor.execute(
        'select locs from elbow where x = ? and y = ? and z = ?', (x, y, z))
    data = cursor.fetchall()
    if len(data) != 0:
        return format_locs(data)
    else:
        return find_locations_with_error(euler, 3)


def find_locations_with_error(euler, error=3):
    x = int(euler[0])
    y = int(euler[1])
    z = int(euler[2])
    cursor.execute(
        'select locs from elbow where x > ? and x < ? and y > ? and y < ? and z > ? and z < ?', (x-error, x+error, y-error, y+error, z-error, z+error))
    data = cursor.fetchall()
    if len(data) == 0:
        return find_locations_with_error(euler, error+1)
    else:
        # print('error range is %d' % error)
        return format_locs(data)


def format_locs(fetch_data):
    res = []
    for d in fetch_data:
        locs = locs_string_to_array(d[0])
        for l in locs:
            res.append(l)
    return np.array(res)

def locs_string_to_array(entry: str):
    temp = entry[1:-1].split(',')
    num = int(len(temp)/3)
    res = np.zeros(shape=(num, 3))
    for i in range(0, num):
        res[i][0] = float(temp[3*i])
        res[i][1] = float(temp[3*i+1])
        res[i][2] = float(temp[3*i+2])
    return res


def data_handler(pre_locs, locs, pre_time, cur_time):
    if len(pre_locs) == 0:
        return [], 0
    row, col = pre_locs.shape[0], locs.shape[0]
    time = cur_time - pre_time
    states = np.zeros((row * col, 3))
    # f = lambda: pre_locs[r in range(0, row)] - locs[c in range(0, col)]
    # states = np.array(f)
    for r in range(0, row):
        for c in range(0, col):
            # states[r * col + c] =
            states[r * col + c] = (pre_locs[r] - locs[c]) / time * 1000
    return states, time


def viterbi(pre_state, cur_state, pre_tt, cur_tt, pre_prob):
    if len(pre_state) == 0:
        return []
    row, col = pre_state.shape[0], cur_state.shape[0]
    print('col = %d, row = %d' % (col, row))
    probs = np.zeros((col, row), dtype='float32')
    if len(pre_prob) == 0:
        pre_prob = np.ones(pre_state.shape[0])
    for r in range(0, row):
        for c in range(0, col):
            if row % 3 == col / 3:
                acc = (cur_state[c] - pre_state[r]) / (pre_tt + cur_tt) * 2
                acc_offset = np.sum((acc - acc_observed) ** 2)
                probs[c, r] = np.exp(acc_offset)
    prob = np.dot(probs, pre_prob)
    ll = locs[np.argmax(prob)]
    ress.append([ll[0],ll[1],ll[2]])
    return prob

csv_reader = csv.reader(open('./resource/watch_data.csv', encoding='utf-8'))
conn = sqlite3.connect('./resource/locs.db')
cursor = conn.cursor()
out = open("./output/res-elbow.csv", "a+", newline="")
csv_writer = csv.writer(out, dialect="excel")

pre_locs = []
locs = []
pre_time = 0
cur_time = 0
pre_state = []
cur_state = []
pre_tt = 0
cur_tt = 0
acc_observed = np.zeros(3)
cur_prob = []
ress = []


for row in csv_reader:
    start_time = timer()
    if len(row) == 7:
        euler = [int(float(row[1])), int(float(row[2])), int(float(row[3]))]
        acc_observed = np.array([float(row[4]), float(row[5]), float(row[6])])
        res = find_locations(euler)
        pre_locs = locs
        locs = np.array(res)
        pre_time = cur_time
        cur_time = int(row[0])
        pre_state, pre_tt = cur_state, cur_tt
        cur_state, cur_tt = data_handler(pre_locs, locs, pre_time, cur_time)
        cur_prob = viterbi(pre_state, cur_state, pre_tt, cur_tt, cur_prob)
    print('this state takes %d second.' % (timer() - start_time))

conn.commit()
conn.close()
ress = np.array(ress)
data_x = ress[:, 0]
data_y = ress[:, 1]
data_z = ress[:, 2]

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(data_x, data_y, data_z)
ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})

plt.show()


# for t in range(0, len(ress)):
#     # csv_writer.writerow(ress[t])
#     print(ress[t])