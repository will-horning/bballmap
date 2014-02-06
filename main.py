import os, sys, json
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Heatmap
from flask import Flask, request, render_template

app = Flask(__name__)

Session = sessionmaker()
db = create_engine("sqlite:///shots.db", 
                    connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()

@app.route("/")
def index():
    teams = session.query(Team).all()
    teams = [[team.id, team] for team in teams]
    return render_template("heatmap.html", teams=teams)
    
def free_throw_filter(shot_rows):
    """
    Returns only rows of Shots table that are NOT free throws or 
    uncontested layups.
    """
    filtered_shot_rows = []
    for shot_row in shot_rows:
        if (not (shot_row[0] == 0 and abs(shot_row[1]) in [28,42]) 
            and ("Free" not in shot_row[3] and "Lay" not in shot_row[3])):
            filtered_shot_rows.append(shot_row)
    return filtered_shot_rows

@app.route('/get_shot_data', methods=['GET'])
def get_shot_data():
    """
    Returns shot totals as json list. 
    """
    testing = True
    player_id = request.args.get('player_id')
    q =  "select xcoord, ycoord, shotresult, " + \
        " shot_type from shots where player_id=" + player_id 
    sqlresponse = session.execute(q)
    shot_rows = [list(row) for row in sqlresponse.fetchall()]
    filtered_shot_rows = free_throw_filter(shot_rows)
    hm = Heatmap(filtered_shot_rows)
    sd = hm.local_shot_totals
    nmin, nmax = min(sd.values()), max(sd.values())
    sd = [[x*hm.cell_w, y * hm.cell_h, (float(n) - nmin) / (nmax - nmin)] for (x, y), n in sd.iteritems()]
    return json.dumps(sd)

@app.route("/gen_heatmap_img", methods=['GET'])
def gen_heatmap_img():
    """
    Generates heatmap image then returns img tag for it. Heatmap image is saved
    to 'static/<player_id>.png'.
    """
    testing = True
    player_id = request.args.get('player_id')
    path = player_id + ".png"
    imtag = "<img src=\"static/" + path + "\">"
    if path not in os.listdir("static/") or testing:
        q =  "select xcoord, ycoord, shotresult, " + \
            " shot_type from shots where player_id=" + player_id 
        sqlresponse = session.execute(q)
        shot_rows = [list(row) for row in sqlresponse.fetchall()]
        i = len(shot_rows)
        filtered_shot_rows = free_throw_filter(shot_rows)
        hm = Heatmap(filtered_shot_rows)
        hm.k_nearest_gen(rdist=4, sd=3.2)
        path = "static/" + path
        hm.im.save(path)
        print path
        return imtag

@app.route("/get_players", methods=['GET'])
def get_players():
    """
    Returns all players with the given team id as json.
    """
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