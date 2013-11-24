import cherrypy, os, sys
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Py_HeatMap

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
    
class Main():
	Session = sessionmaker()
	db = create_engine("sqlite:///shots.db")
	Session.configure(bind=db)
	session = Session()

	def index(self):
		f = open("heatmap.html", "r")
		html = f.read()
		f.close()
		return html
	index.exposed = True

	def foul_shot_filter(self, shot_rows):
		filtered_shot_rows = []
		for shot_row in shot_rows:
			if ("Free" not in shot_row[3] and
				"Lay" not in shot_row[3]):
				filtered_shot_rows.append(shot_row)
		return filtered_shot_rows

	def gen_heatmap_img(self, player_ids="", halve_court=0, sd=2.3, rdist=8):
		testing = True
		if isinstance(player_ids, list):
			player_ids = [int(pid) for pid in player_ids]
		else:
			player_ids = [int(player_ids)]
		path = str(player_ids) + "_" + str(halve_court) + ".bmp"
		imtag = "<img src=\"static/" + path + "\">"
		if path not in os.listdir("static/") or testing:
			q =  "select xcoord, ycoord, shotresult, " + \
				" shot_type from shots where " + \
				 " or ".join(["player_id=" + str(i) for i in player_ids])
			sqlresponse = self.session.execute(q)
			shot_rows = [list(row) for row in sqlresponse.fetchall()]
			filtered_shot_rows = self.foul_shot_filter(shot_rows)
			hm = Py_HeatMap(filtered_shot_rows, PATH_TO_COURT_IMG)
			hm.generate_heatmap_image()
			path = "static/" + path
			hm.im.save(path, "JPEG")
			del hm
			return imtag
	gen_heatmap_img.exposed = True

	def get_teams(self):
		json_teams = []
		teams = self.session.query(Team).all()
		for team in teams:
			json_team = "{'id': " + str(team.id) + ", 'name': '" + team.name + "'}"
			json_teams.append(json_team)
		return "{\"teams\": [" + ",".join(json_teams) + "]}"

	get_teams.exposed = True

	def get_players(self, team_id=""):
		tid = int(team_id[4:])
		json_players = []
		team = self.session.query(Team).filter_by(id = tid).first()
		players = team.players
		for player in players:
			name = player.firstname + " " + player.lastname
			name = name.replace("'", "")
			json_player = "{'id': " + str(player.id) + ", 'name': '" + name + "'}"
			json_players.append(json_player)
		return "{\"players\": [" + ",".join(json_players) + "]}"
	get_players.exposed = True


conf = {"/": {"tools.staticdir.root": os.getcwd()},
        "/static": {"tools.staticdir.on": True,
                    "tools.staticdir.dir": "static"}
        }

cherrypy.server.socket_port = 8000
cherrypy.server.socket_host = "127.0.0.1"
cherrypy.quickstart(Main(), config=conf)

