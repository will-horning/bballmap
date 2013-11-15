import datetime, urllib2, re
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from models import Player, Shot, Team

Session = sessionmaker()
db = create_engine("sqlite:///shots.db")
Session.configure(bind=db)
session = Session()


base_scoreboard_url = "http://www.cbssports.com/nba/scoreboard/"
scoreboard_urls = []

x=0
current_date = datetime.date.today()
while current_date.year > 2011:
    x+=1
    scoreboard_urls.append(base_scoreboard_url + str(current_date).replace("-", ""))    
    current_date -= datetime.timedelta(days=1)
    print "day " + str(x)

gametracker_urls = set()

for url in scoreboard_urls:
    try:
        html = urllib2.urlopen(url).read()
        links = re.findall('''href=["'](.[^"']+)["']''', html)    
        gametracker_urls |= set(["http://www.cbssports.com" + l for l in links if "gametracker/live" in l])
    except urllib2.HTTPError:
        continue
    
def extract_shotdata(html):
    shot_data_start = 'shotData: "'
    shot_data_end = "awayScoringData"
    i1 = html.find(shot_data_start) + len(shot_data_start)
    i2 = html.find(shot_data_end)
    for shot_data_string in html[i1:i2].strip().split("~"):
        session.add(Shot(shot_data_string))
    
def extract_player_ids(html):
    names2pids = {}
    awaystart = 'awayScoringData: "'
    homestart = 'homeScoringData: "'
    awayteamstart = '"awayTeam fontUbuntuBold">'
    hometeamstart = '"homeTeam fontUbuntuBold">'
    i1 = html.find(awaystart) + len(awaystart)
    i2 = html.find('"', i1)
    away_data = html[i1:i2].split("|")
    i1 = html.find(homestart) + len(homestart)
    i2 = html.find('"', i1)
    home_data = html[i1:i2].split("|")
    away_data = [s[:s.find(",")] for s in away_data]
    home_data = [s[:s.find(",")] for s in home_data]
    i1 = html.find(awayteamstart) + len(awayteamstart)
    i2 = html.find('<', i1)
    away_team_name = html[i1:i2]
    i1 = html.find(hometeamstart) + len(hometeamstart)
    i2 = html.find('<', i1)
    home_team_name = html[i1:i2]
    home_team = session.query(Team).filter(Team.name == home_team_name).first()
    away_team = session.query(Team).filter(Team.name == away_team_name).first()
    if not home_team:
        session.add(Team(home_team_name))
        home_team = session.query(Team).filter(Team.name == home_team_name).first()
    if not away_team:
        session.add(Team(away_team_name))
        away_team = session.query(Team).filter(Team.name == away_team_name).first()
    def f(player_data, team_id):
        for player_data_string in player_data:
            pid, name = player_data_string.split(":")
            pid = int(pid)
            if "\xa0" in name: name = name.replace("\xa0", " ")
            if "&nbsp" in name: name = name.replace("&nbsp;", " ").split(" ", 1)
            if len(name) == 1:
                fname = name[0]
                lname = ""
            else:
                fname, lname = name[0], "".join(name[1:])
            if not session.query(Player).get(pid):
                session.add(Player(pid, fname, lname, team_id))
    f(away_data, away_team.id)
    f(home_data, home_team.id)

while gametracker_urls:
	url = gametracker_urls.pop()
	try:
		tml = urllib2.urlopen(url).read()
		extract_shotdata(tml)
		extract_player_ids(tml)
	except urllib2.URLError:
		print url
	print len(gametracker_urls)
    
session.commit()



