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
        'select locs from wrist where x = ? and y = ? and z = ?', (x, y, z))
    data = cursor.fetchall()
    if len(data) != 0:
        return format_locs(data)
    else:
        return find_locations(euler, 3)


def find_locations(euler, error=3):
    x = int(euler[0])
    y = int(euler[1])
    z = int(euler[2])
    cursor.execute(
        'select locs from wrist where x > ? and x < ? and y > ? and y < ? and z > ? and z < ?', (x-error, x+error, y-error, y+error, z-error, z+error))
    data = cursor.fetchall()
    if len(data) == 0:
        return find_locations(euler, error+1)
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


csv_reader = csv.reader(open('./resource/watch_data.csv', encoding='utf-8'))
conn = sqlite3.connect('./resource/locs.db')
cursor = conn.cursor()
out = open("./output/res-elbow.csv", "a+", newline="")
csv_writer = csv.writer(out, dialect="excel")

draw_data = []

for row in csv_reader:
    tt = timer()
    if len(row) == 7:
        euler = [int(float(row[1])), int(float(row[2])), int(float(row[3]))]
        locs = find_locations(euler)
        ll = np.average(locs, 0)
        # print(type(ll))
        print('euler is (%d,%d,%d), loc is (%f, %f, %f)' %
              (euler[0], euler[1], euler[2], ll[0], ll[1], ll[2]))
        draw_data.append([ll[0], ll[1], ll[2]])
        # print(ll.shape)
        # print('%f, %f, %f' % (ll[0], ll[1], ll[2]))

        # csv_writer.writerow(ll)
    # print(timer()-tt)

conn.commit()
conn.close()
draw_data = np.array(draw_data)
data_x = draw_data[:, 0]
data_y = draw_data[:, 1]
data_z = draw_data[:, 2]

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(data_x, data_y, data_z)

ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})

plt.show()
