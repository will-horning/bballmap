import cherrypy, os, sys, json, math
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import numpy as np
from collections import defaultdict
from sklearn import linear_model
import matplotlib.cm as cm
import matplotlib.pyplot as plt

def free_throw_filter(shot_rows):
    filtered_shot_rows = []
    for shot_row in shot_rows:
        if not (shot_row[0] == 0 and abs(shot_row[1]) in [28,42]) and ("Free" not in shot_row[3] and "Lay" not in shot_row[3]):
            filtered_shot_rows.append(shot_row)
    return filtered_shot_rows

PATH_TO_COURT_IMG = "static/nbagrid.bmp"

Session = sessionmaker()
db = create_engine("sqlite:///shots.db", connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()
# pid = 6457 # ray allen
pid = 6496 # kobe
q =  "select xcoord, ycoord, shotresult, " + \
    " shot_type from shots where player_id=" + str(pid) +";" 
sqlresponse = session.execute(q)
shot_rows = [list(row) for row in sqlresponse.fetchall()]
shot_rows = free_throw_filter(shot_rows)

grid_w, grid_h = 50.0, 94.0
m = defaultdict(lambda: [0, 0])
shot_data = [[int(i[0]), int(i[1]), int(i[2])] for i in shot_rows]
for x1, x2, shot_made in shot_data:
    x1, x2 = grid_w / 2 + x1, grid_h / 2 + x2
    if x2 > grid_h / 2: x1, x2 = grid_w - x1, grid_h - x2
    if x1 >= grid_w: x1 -= 1
    if x2 >= grid_h / 2: x2 -= 1
    m[(x1,x2)][1] += 1
    if shot_made: m[(x1,x2)][0] += 1

X, Y = [], []
for k, v in m.iteritems():
    X.append(list(k))
    Y.append(float(v[0]) / v[1])

for x in X:
    # x += [x[0]**2, x[1]**2, x[0]*x[1], x[0]**3, x[1]**3]
    x += [x[0]**n for n in range(2,10)]
    x += [x[1]**n for n in range(2,10)]


X = np.mat(X)
Y = np.mat(Y).T

X, Xtest = X[:-400], X[-400:]
Y, Ytest = Y[:-400], Y[-400:]

def normal_eq(X, Y):
    return ((X.T * X).I * X.T) * Y

def h(theta, xi):
    return xi * theta

z = np.zeros((50, 48))
t = normal_eq(X,Y)
for i in range(len(Y)):
    z[X[i,0], X[i, 1]] = h(t, X[i])

error = []
for i in range(len(Ytest)):
    error.append((h(t, Xtest[i]) - Ytest[i])**2)
error = float(sum(error)) / len(Ytest)
# def cost(theta, X, Y):
#     return 0.5 * len(X) * sum((np.dot(theta, xi) - yi)**2 for xi, yi in izip(X, Y))



plt.imshow(z, extent=(0, 50, 0, 47), interpolation="nearest", cmap=cm.gist_rainbow)
