import cherrypy, os, sys
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Py_HeatMap

PATH_TO_COURT_IMG = "/home/will/code/newballa/static/nbagrid.bmp"

Session = sessionmaker()
db = create_engine("sqlite:///shots.db")
Session.configure(bind=db)
session = Session()

def gen_heatmap_img(id, halve_court=0, sd=2.3, rdist=8):
	path = str(id) + "_" + "0" + ".bmp"
	imtag = "<img src=\"static/" + path + "\">"
	q =  "select xcoord, ycoord, shotresult, " + \
		" shot_type from shots where " + \
		"player_id=" + str(id)
	sqlresponse = session.execute(q)
	shot_rows = [list(row) for row in sqlresponse.fetchall()]
	filtered_shot_rows = []
	for shot_row in shot_rows:
		if ("Free" not in shot_row[3] and
			"Lay" not in shot_row[3]):
			filtered_shot_rows.append(shot_row)
	hm = Py_HeatMap(filtered_shot_rows, PATH_TO_COURT_IMG)
	hm.generate_heatmap_image()
	path = "static/" + path
	hm.im.save(path, "JPEG")
	del hm

players = session.query(Player).all()
for player in players:
	print player.n_shots
	if player.n_shots > 400:
		print player
		gen_heatmap_img(player.id)
		
