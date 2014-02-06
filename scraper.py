from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from bs4 import BeautifulSoup
import datetime, re, requests

name2abbrev = { 'Milwaukee': 'MIL',
                'Miami': 'MIA',
                'Atlanta': 'ATL',
                'Boston': 'BOS',
                'Detroit': 'DET',
                'Denver': 'DEN',
                'New York': 'NY',
                'Sacramento': 'SAC',
                'Brooklyn': 'BKN',
                'Portland': 'POR',
                'Toronto': 'TOR',
                'Oklahoma City': 'OKC',
                'Cleveland': 'CLE',
                'Charlotte': 'CHA',
                'Utah': 'UTA',
                'Golden State': 'GS',
                'Chicago': 'CHI',
                'Houston': 'HOU',
                'Washington': 'WAS',
                'LA Lakers': 'LAL',
                'LA Clippers': 'LAC',
                'Philadelphia': 'PHI',
                'Phoenix': 'PHO',
                'Memphis': 'MEM',
                'New Orleans': 'NO',
                'Dallas': 'DAL',
                'Orlando': 'ORL',
                'Indiana': 'IND',
                'San Antonio': 'SA',
                'Minnesota': 'MIN',
                'New Jersey': 'NJ'
                }

Session = sessionmaker()
db = create_engine("sqlite:///shots.db",
                    connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()

ncaa_url = "http://www.cbssports.com/collegebasketball/scoreboard/div1/"
nba_url = "http://www.cbssports.com/nba/scoreboard/"
nba_gt_url = "http://www.cbssports.com/nba/gametracker/live/NBA_"
today = datetime.date.today()

def scrape(n_years):
    for g_url, series_n in get_game_urls(n_years):
        get_shot_data(g_url, series_n)

def get_game_urls(n_years):
    for k in xrange(1109, 365*n_years):
        game_date = (today - datetime.timedelta(days=k))
        espn_base_url = "http://espn.go.com/nba/schedule?date="
        schedule_url = espn_base_url + game_date.strftime('%Y%m%d')
        soup = BeautifulSoup(requests.get(schedule_url).text)
        print schedule_url
        topdiv = soup.find('div', {'id': 'my-teams-table'})
        rows = topdiv.div.div.table.findAll('tr')
        rows = [r for r in rows[2:] if 'oddrow' in r['class'] or 'evenrow' in r['class']]
        rows = [r for r in rows if r.td.a]
        for row in rows:
            if 'postponed' in str(row).lower(): continue
            if 'no games' in str(row).lower(): continue
            if 'canceled' in str(row).lower(): continue
            ht, at = row.td.a.contents[0].split(', ')
            if 'conf' in at.lower(): continue
            try:
                at = name2abbrev[re.search(r'(\D+)', at).group(1).strip()]
                ht = name2abbrev[re.search(r'(\D+)', ht).group(1).strip()]
            except KeyError:
                print row.td.a
                print at, ht
            series_n = '0'
            if row.td.br:
                series_n = re.match('.*(\d+)', row.td.contents[2]).group(1)
            game_id = '%s_%s@%s' % (game_date.strftime('%Y%m%d'), ht, at)
            yield nba_gt_url + game_id, series_n
            game_id = '%s_%s@%s' % (game_date.strftime('%Y%m%d'), at, ht)
            yield nba_gt_url + game_id, series_n

def get_shot_data(game_url, series_n):
    r = requests.get(game_url)
    if r.history: return #redirect, so url is incorrect
    print game_url
    html = r.text
    awaydata = re.search(r'awayScoringData: "(.*?)"', html).group(1).split("|")
    homedata = re.search(r'homeScoringData: "(.*?)"', html).group(1).split("|")
    awayname, homename = re.search(r'[->] ?(.*?) vs. (.*?) -', html).groups()
    away_team = process_team_data(awayname, awaydata)
    home_team = process_team_data(homename, homedata)
    date_string = re.search(r'NBA_(\d{8})', html).group(1)
    shot_data = re.search(r'shotData: "(.*?)\s', html).group(1)
    g_time = datetime.datetime(int(date_string[:4]), int(date_string[4:6]), int(date_string[6:8]), 0, 0, 0)
    g = Game(home_team, away_team, g_time, series_n)
    for shot_data_string in shot_data.strip().split("~"):
        if shot_data_string.count(',') > 4:
            p = session.query(Player).filter_by(id=int(shot_data_string.split(',')[3])).first()
            session.add(Shot(shot_data_string, date_string, g, p))
        else: print shot_data_string
    session.commit()

def process_team_data(team_name, player_data):
    t = session.query(Team).filter_by(name=team_name).first()
    if not t: 
        t = Team(team_name)
        session.add(t)
    for s in player_data:
        player_id, p_name = re.search(r'(\d*):(.*?),', s).groups()
        if not session.query(Player).filter_by(id=player_id).first():
            if "&nbsp" in p_name: p_name = p_name.replace("&nbsp;", " ")
            session.add(Player(player_id, p_name, t))
    session.commit()
    return t

# def get_abbrevs(n_years):
#     for k in xrange(1, 365*n_years):
#         game_date = (today - datetime.timedelta(days=k))
#         scoreboard_url = ncaa_url + game_date.strftime('%Y%m%d')
#         print scoreboard_url
#         html = requests.get(scoreboard_url).text
#         soup = BeautifulSoup(html)
#         scoreboarddivs = [div for div in soup.findAll('div') if 'scoreBox' in div['class']]
#         for div in scoreboarddivs:
#             div.table.findAll('tr')

# def get_ncaa_game_urls(n_years):
#     for k in xrange(1, 365 * n_years):
#         game_date = (today - datetime.timedelta(days=k))
#         espn_base_url = "http://espn.go.com/mens-college-basketball/schedule?date="
#         schedule_url = espn_base_url + game_date.strftime('%Y%m%d')
#         soup = BeautifulSoup(requests.get(schedule_url).text)
#         topdiv = soup.find('div', {'id': 'my-teams-table'})
#         rows = topdiv.div.div.table.findAll('tr')
#         if 'Top 25' not in str(rows[0]): continue
#         for row in rows[2:]:
#             print row['class']
#             if row['class'] == 'stathead' or len(row.td.findAll('a')) < 2: break
#             elif 'oddrow' in row['class'] or 'evenrow' in row['class']:
#                 ht = row.td.findAll('a')[0].contents[0]
#                 at = row.td.findAll('a')[1].contents[0]
#                 game_id = '%s_%s@%s' % (game_date.strftime('%Y%m%d'), at, ht)
#                 yield game_id 
                
# def get_ncaa_tournament_urls(start_date, n_years):
#     base_url = 'http://www.cbssports.com/collegebasketball/scoreboard/ncaa-tournament/'
#     for k in xrange(365 * n_years):
#         date = (start_date - datetime.timedelta(days=k))
#         if date.month in [3,4]:
#             yield base_url + str(date).replace('-', '')
