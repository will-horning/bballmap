import os, sys, json
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Heatmap
from flask import Flask, request, render_template

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
    
app = Flask(__name__)

Session = sessionmaker()
db = create_engine("sqlite:///shots2.db", connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()

@app.route("/")
def index():
    teams = session.query(Team).all()
    teams = [[team.id, team] for team in teams]
    return render_template("heatmap.html", teams=teams)
    
def free_throw_filter(shot_rows):
    """
    Returns only rows of Shots table that are NOT free throws or uncontested layups.
    """
    filtered_shot_rows = []
    for shot_row in shot_rows:
        if not (shot_row[0] == 0 and abs(shot_row[1]) in [28,42]) and ("Free" not in shot_row[3] and "Lay" not in shot_row[3]):
            filtered_shot_rows.append(shot_row)
    return filtered_shot_rows

@app.route("/gen_heatmap_img", methods=['GET'])
def gen_heatmap_img():
    """
    :param player_ids: Either string or int that will contain one or more player ids. If multiple
    id's are input they heatmap produced will use shots taken by all the included
    players.

    :keyword sd: Standard deviation for the normal curve plotted around shot locations.

    :keyword rdist: Radial distance from a shot for the normal curve to encompass. Bigger rdist means more
    smoothed distribution plot.

    :returns: The img tag for the finished heatmap img, as a string.
    """
    rdist = 3
    sd = float(request.args.get('sd'))
    testing = True
    player_id = request.args.get('player_id')
    path = player_id + ".gif"
    imtag = "<img src=\"static/" + path + "\">"
    if path not in os.listdir("static/") or testing:
        q =  "select xcoord, ycoord, shotresult, " + \
            " shot_type from shots where player_id=" + player_id 
        sqlresponse = session.execute(q)
        shot_rows = [list(row) for row in sqlresponse.fetchall()]
        i = len(shot_rows)
        filtered_shot_rows = free_throw_filter(shot_rows)
        hm = Heatmap(filtered_shot_rows)
        # hm.generate_heatmap(rdist, sd)
        hm.old_gen_hm()
        path = "static/" + path
        hm.im.save(path, "gif")
        return imtag

@app.route("/get_players", methods=['GET'])
def get_players():
    """ Returns all the players on the given team in JSON."""
    tid = int(request.args.get('team_id')[4:])
    json_players = []
    t = session.query(Team).filter_by(id = tid).first()
    t.players
    for player in t.players:
        if player.n_shots > 400:
            name = player.full_name
            name = name.replace("'", "")
            json_players.append({'id': player.id, 'name': name})
    return json.dumps({'teamname': t.name, 'players': json_players})

if __name__ == "__main__":
    app.debug == True
    app.run()