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
while current_date.year > 2009:
	x+=1
	scoreboard_urls.append(base_scoreboard_url + str(current_date).replace("-", ""))	
	current_date -= datetime.timedelta(days=1)
gametracker_urls = set()

for url in scoreboard_urls:
	try:
		html = urllib2.urlopen(url).read()
		links = re.findall('''href=["'](.[^"']+)["']''', html)	
		gametracker_urls |= set(["http://www.cbssports.com" + l for l in links if "gametracker/live" in l])
	except urllib2.HTTPError:
		continue
	
def extract_shotdata(html):
	date_string = re.search(r'NBA_(\d{8})', html).group(1)
	shot_data = re.search(r'shotData: "(.*?)\s', html).group(1)
	if shot_data:
		for shot_data_string in shot_data.strip().split("~"):
			session.add(Shot(shot_data_string, date_string))
	else:
		f = open("foo.txt", "w")
		f.write(html)
		f.close()
		assert False
		
def extract_player_ids(html):
	away_data = re.search(r'awayScoringData: "(.*?)"', html).group(1).split("|")
	home_data = re.search(r'homeScoringData: "(.*?)"', html).group(1).split("|")
	away_team_name, home_team_name = re.search(r'[->] ?(.*?) vs. (.*?) -', html).groups()

	def f(team_name, player_data):
		player_team = session.query(Team).filter(Team.name == team_name).first()
		if not player_team:
			session.add(Team(team_name))
			player_team = session.query(Team).filter(Team.name == team_name).first()
		for s in player_data:
			player_id, player_name = re.search(r'(\d*):(.*?),', s).groups()
			player_id = int(player_id)
			if "\xa0" in player_name: player_name = player_name.replace("\xa0", " ")
			if "&nbsp" in player_name: player_name = player_name.replace("&nbsp;", " ").split(" ", 1)
			if len(player_name) == 1:
				fname = player_name[0]
				lname = ""
			else:
				fname, lname = player_name[0], "".join(player_name[1:])
			if not session.query(Player).get(player_id):
				session.add(Player(player_id, fname, lname, player_team.id))
	f(away_team_name, away_data)
	f(home_team_name, home_data)

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



