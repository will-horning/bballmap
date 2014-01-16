import cherrypy, os, sys, json
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Heatmap

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
    
class Main():
	Session = sessionmaker()
	db = create_engine("sqlite:///shots.db", connect_args={'check_same_thread':False})
	Session.configure(bind=db)
	session = Session()

	def index(self):
		f = open("heatmap.html", "r")
		html = f.read()
		f.close()
		return html
	index.exposed = True

	def free_throw_filter(self, shot_rows):
		"""
		Returns only rows of Shots table that are NOT free throws or uncontested layups.
		"""
		filtered_shot_rows = []
		for shot_row in shot_rows:
			if not (shot_row[0] == 0 and abs(shot_row[1]) in [28,42]) and ("Free" not in shot_row[3] and "Lay" not in shot_row[3]):
				filtered_shot_rows.append(shot_row)

		return filtered_shot_rows

	def gen_heatmap_img(self, player_ids="", sd=2.3, rdist=8):
		"""
		:param player_ids: Either string or int that will contain one or more player ids. If multiple
		id's are input they heatmap produced will use shots taken by all the included
		players.

		:keyword sd: Standard deviation for the normal curve plotted around shot locations.

		:keyword rdist: Radial distance from a shot for the normal curve to encompass. Bigger rdist means more
		smoothed distribution plot.

		:returns: The img tag for the finished heatmap img, as a string.
		"""
		if player_ids == "": return ""
		testing = True
		if isinstance(player_ids, list):
			player_ids = [int(pid) for pid in player_ids]
		else:
			player_ids = [int(player_ids)]
		path = str(player_ids) + "_" + ".gif"
		imtag = "<img src=\"static/" + path + "\">"
		if path not in os.listdir("static/") or testing:
			q =  "select xcoord, ycoord, shotresult, " + \
				" shot_type from shots where " + \
				 " or ".join(["player_id=" + str(i) for i in player_ids]) 
			sqlresponse = self.session.execute(q)
			shot_rows = [list(row) for row in sqlresponse.fetchall()]
			i = len(shot_rows)
			filtered_shot_rows = self.free_throw_filter(shot_rows)
			hm = Heatmap(filtered_shot_rows)
			hm.generate_heatmap()
			path = "static/" + path
			hm.im.save(path, "gif")
			return imtag
	gen_heatmap_img.exposed = True

	def get_teams(self):
		""" Returns all team names in JSON. """
		teams = self.session.query(Team).all()
		return json.dumps({'teams': [{'id': t.id, 'name': t.name} for t in teams]})
	get_teams.exposed = True

	def get_players(self, team_id=""):
		""" Returns all the players on the given team in JSON."""
		tid = int(team_id[4:])
		json_players = []
		t = self.session.query(Team).filter_by(id = tid).first()
		t.players
		for player in t.players:
			if player.n_shots > 400:
				name = player.firstname + " " + player.lastname
				name = name.replace("'", "")
				json_players.append({'id': player.id, 'name': name})
		return json.dumps({'teamname': t.name, 'players': json_players})
	get_players.exposed = True


conf = {"/": {"tools.staticdir.root": os.getcwd()},
        "/static": {"tools.staticdir.on": True,
                    "tools.staticdir.dir": "static"}
        }

cherrypy.server.socket_port = 8000
cherrypy.server.socket_host = "127.0.0.1"
cherrypy.quickstart(Main(), config=conf)

