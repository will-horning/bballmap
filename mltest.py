import cherrypy, os, sys, json
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import numpy as np
from collections import defaultdict
from sklearn import linear_model

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
pid = 6457 # ray allen

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
    if x1 >= grid_w: x1 -= 1
    if x2 >= grid_h: x2 -= 1
    if x2 > grid_h / 2: x1, x2 = grid_w - x1, grid_h - x2
    m[(x1,x2)][1] += 1
    if shot_made: m[(x1,x2)][0] += 1

X, Y = [], []
for k, v in m.iteritems():
    X.append(list(k))
    Y.append(float(v[0]) / v[1])

X = np.array(X)
Y = np.array(Y)  

lr = linear_model.LinearRegression()
o = lr.fit(X, Y)
