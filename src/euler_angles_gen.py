import numpy as np
import math
import sqlite3
lu = 0.3
lf = 0.23
index_length = 360 * 360 * 360


def euler_angles_and_loc_gen(a1, a2, a3, a4, a5):
    a1 = math.pi / 180 * a1
    a2 = math.pi / 180 * a2
    a3 = math.pi / 180 * a3
    a4 = math.pi / 180 * a4
    a5 = math.pi / 180 * a5
    Rot1 = np.array([[np.cos(a1) * np.cos(a3) + np.sin(a1) * np.sin(a2) * np.sin(a3),
                      np.cos(a3) * np.sin(a1) * np.sin(a2) - np.cos(a1) * np.sin(a3), np.cos(a2) * np.sin(a1)],
                     [np.cos(a2) * np.sin(a3), np.cos(a2)
                      * np.cos(a3), -np.sin(a2)],
                     [np.cos(a1) * np.sin(a2) * np.sin(a3) - np.sin(a1) * np.cos(a3), np.sin(a1)
                      * np.sin(a3) + np.cos(a1) * np.cos(a3) * np.sin(a2), np.cos(a1) * np.cos(a2)]
                     ])
    Rot2 = np.array([[np.cos(a4), np.sin(a4) * np.sin(a5), np.sin(a4)*np.cos(a5)],
                     [0, np.cos(a5), -np.sin(a4)],
                     [-np.sin(a4), np.cos(a4)
                      * np.sin(a5), np.cos(a4)*np.cos(a5)]
                     ])
    Rot3 = np.dot(Rot1, Rot2)
    l1 = np.array([[0], [0], [-lu]])
    l2 = np.array([[lf], [0], [0]])

    elbow = np.dot(Rot1, l1)
    elbow2wrist = np.dot(Rot3, l2)
    wrist = elbow + elbow2wrist
    euler = [0, 0, 0]
    if Rot3[2][2] == 0:
        euler[0] = 180
    else:
        euler[0] = round(np.arctan(Rot3[2][0] / Rot3[2][2]) / math.pi * 180)
    if np.abs(Rot3[1][2]) == 1:
        euler[1] = 180
    else:
        euler[1] = round(
            np.arctan(-Rot3[1][2] / (np.sqrt(1 - Rot3[1][2] * Rot3[1][2]))) / math.pi * 180)
    if Rot3[1][1] == 0:
        euler[2] = 180
    else:
        euler[2] = round(np.arctan(Rot3[1][0] / Rot3[1][1]) / math.pi * 180)

    return euler, elbow, wrist


def point_cloud_gen():
    for an1 in range(0, 91, 10):
        print(an1)
        for an2 in range(0, 91, 10):
            for an3 in range(0, 91, 10):
                for an4 in range(-90, 90, 1):
                    for an5 in range(0, 91, 10):
                        euler, elbow, wrist = euler_angles_and_loc_gen(
                            an1, an2, an3, an4, an5)
                        index = euler_to_index(euler)
                        # point_cloud_elbow[index].append(elbow)
                        index_string = str(index)
                        if index_string not in elbow_array.keys():
                            elbow_array[index_string] = [
                                elbow[0][0], elbow[1][0], elbow[2][0]]
                            wrist_array[index_string] = [
                                wrist[0][0], wrist[1][0], wrist[2][0]]

                        else:
                            elbow_array[index_string].append(elbow[0][0])
                            elbow_array[index_string].append(elbow[1][0])
                            elbow_array[index_string].append(elbow[2][0])
                            wrist_array[index_string].append(wrist[0][0])
                            wrist_array[index_string].append(wrist[1][0])
                            wrist_array[index_string].append(wrist[2][0])


def euler_to_index(euler):
    x = int(euler[0]) + 180
    y = int(euler[1]) + 180
    z = int(euler[2]) + 180
    index = x * 360 * 360 + y * 360 + z
    if index < 0 or index >= index_length:
        print('euler is out of index')
    return index % index_length


def index_to_euler(index: int):
    temp = index
    z = (temp % 360)-180
    temp /= 360
    temp = int(temp)
    y = (temp % 360)-180
    temp /= 360
    temp = int(temp)
    x = (temp % 360)-180
    return (x, y, z)

# Initialization database connection
conn = sqlite3.connect('./resource/locs.db')
cursor = conn.cursor()
# Initialing dictory
elbow_array = dict()
wrist_array = dict()

point_cloud_gen()

for key in elbow_array.keys():
    data = elbow_array[key]
    euler = index_to_euler(int(key))
    cursor.execute('insert into elbow values (?,?,?,?)',
                   (euler[0], euler[1], euler[2], str(data)))

for key in wrist_array.keys():
    data = wrist_array[key]
    euler = index_to_euler(int(key))
    cursor.execute('insert into wrist values (?,?,?,?)',
                   (euler[0], euler[1], euler[2], str(data)))
# commit operation is neccery or it would not write into our db otherwise
conn.commit()
conn.close()
