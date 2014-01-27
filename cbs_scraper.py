from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *

import datetime, re, requests

Session = sessionmaker()
db = create_engine("sqlite:///shots2.db", 
                    connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()

cbs_url = "http://www.cbssports.com"
ncaa_url = "http://www.cbssports.com/collegebasketball/scoreboard/div1/"
nba_url = "http://www.cbssports.com/nba/scoreboard/"
date = datetime.date.today()
n_years = 8
start_urls = []

for k in xrange(100):
    url = nba_url + str(date - datetime.timedelta(days=k))
    start_urls.append(url.replace('-',''))

def get_gametracker_urls(schedule_url):
    html = requests.get(schedule_url).text
    urls = re.findall(r'href=[\'"]?([^\'" >]+)', html)
    return (cbs_url + url for url in urls if 'gametracker/live' in url)

def get_shot_data(game_url):
    html = requests.get(game_url).text
    awaydata = re.search(r'awayScoringData: "(.*?)"', html).group(1).split("|")
    homedata = re.search(r'homeScoringData: "(.*?)"', html).group(1).split("|")
    awayname, homename = re.search(r'[->] ?(.*?) vs. (.*?) -', html).groups()
    away_team = process_team_data(awayname, awaydata)
    home_team = process_team_data(homename, homedata)
    date_string = re.search(r'NBA_(\d{8})', html).group(1)
    shot_data = re.search(r'shotData: "(.*?)\s', html).group(1)
    g_time = datetime.datetime(int(date_string[:4]), int(date_string[4:6]), int(date_string[6:8]), 0, 0, 0)
    g = Game(home_team, away_team, g_time)
    for shot_data_string in shot_data.strip().split("~"):
        if shot_data_string.count(',') > 4:
            p = session.query(Player).filter_by(id=int(shot_data_string.split(',')[3])).first()
            session.add(Shot(shot_data_string, date_string, g, p))
        else: print shot_data_string

def process_team_data(team_name, player_data):
    t = session.query(Team).filter_by(name=team_name).first()
    if not t: 
        t = Team(team_name)
        session.add(t)
    for s in player_data:
        player_id, p_name = re.search(r'(\d*):(.*?),', s).groups()
        if not session.query(Player).filter_by(id=player_id).first():
            # if "\xa0" in p_name: p_name = p_name.replace("\xa0", " ")
            if "&nbsp" in p_name: p_name = p_name.replace("&nbsp;", " ")
            session.add(Player(player_id, p_name, t))
    return t

for start_url in start_urls:
    for game_url in get_gametracker_urls(start_url):
        get_shot_data(game_url)
