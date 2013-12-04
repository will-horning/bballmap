from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relation, backref
import datetime

db = create_engine("sqlite:///shots.db")
Base = declarative_base()

QUARTER_LENGTH_IN_MIN = 12 # Used for converting game time to absolute time.


# Shot types are recorded in CBS Sports data as an integer corresponding to these values:
shot_type_map = {}
shot_type_map[0] = "Shot"
shot_type_map[1] = "Jump Shot"
shot_type_map[2] = "Running Jump"
shot_type_map[3] = "Hook Shot"
shot_type_map[4] = "Tip-in"
shot_type_map[5] = "Layup"
shot_type_map[6] = "Driving Layup"
shot_type_map[7] = "Dunk Shot"
shot_type_map[8] = "Slam Dunk"
shot_type_map[9] = "Driving Dunk"
shot_type_map[10] = "Free Throw"
shot_type_map[11] = "1st of 2 Free Throws"
shot_type_map[12] = "2nd of 2 Free Throws"
shot_type_map[13] = "1st of 3 Free Throws"
shot_type_map[14] = "2nd of 3 Free Throws"
shot_type_map[15] = "3rd of 3 Free Throws"
shot_type_map[16] = "Technical Free Throw"
shot_type_map[17] = "1st of 2 Free Throws"
shot_type_map[18] = "2nd of 2 Free Throws"
shot_type_map[19] = "Finger Roll"
shot_type_map[20] = "Reverse Layup"
shot_type_map[21] = "Turnaround Jump Shot"
shot_type_map[22] = "Fadeaway Jump Shot"
shot_type_map[23] = "Floating Jump Shot"
shot_type_map[24] = "Leaning Jump Shot"
shot_type_map[25] = "Mini Hook Shot"

    
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
    
class Player(Base):
	__tablename__ = "players"

	id = Column(Integer, primary_key=True)
	firstname = Column(String)
	lastname = Column(String)
	team_id = Column(Integer, ForeignKey("teams.id"))
	team = relation(Team, backref=backref("players", order_by=id))
	n_shots = Column(Integer)

	def __init__(self, pid, fname, lname, team_id):
		self.id = pid
		self.firstname = fname
		self.lastname = lname
		self.team_id = team_id

	def __repr__(self):
		return self.firstname + " " + self.lastname + " " + str(self.id)

class Shot(Base):
	__tablename__ = "shots"
	id = Column(Integer, primary_key=True)
	shotresult = Column(Integer)
	datetime = Column(DateTime)
	quarter = Column(Integer)
	player_id = Column(Integer, ForeignKey("players.id"))
	player = relation(Player, backref=backref("shots", order_by=id))
	shot_type = Column(String(50))
	xcoord = Column(Integer)
	ycoord = Column(Integer)
	distance = Column(Integer)
	homeaway = Column(String(4))
	
	def __repr__(self):
		ret = []
		if self.shotresult: ret = ["Made"]
		else: ret = ["Missed"]
		ret += [" shot by ", self.player.firstname + " " + self.player.lastname]
		return "".join(ret)

	def __init__(self, shot_data_string, date_string):
		shot_data = shot_data_string.split(",")
		self.shotresult = int(shot_data[0])
		self.quarter = int(shot_data[2])
		self.datetime = self.get_absolute_time(shot_data[1], date_string)
		self.player_id = int(shot_data[3])
		self.shot_type = shot_type_map[int(shot_data[5])]
		self.xcoord = int(shot_data[6])
		self.ycoord = int(shot_data[7])
		self.distance = int(shot_data[8].replace('"', ''))

	def get_absolute_time(self, game_time_string, date_string):
		"""
		CBS Sports data records the time for a shot as the time remaining in the current quarter.
		This function converts the game time string to a datetime instance recording the exact time and
		date the shot was taken (for now the hour field is left to zero).
		"""
		minutes_remaining = 0
		seconds_remaining = 0
		if ":" in game_time_string:
			minutes_remaining = int(game_time_string.split(":")[0])
			seconds_remaining = int(game_time_string.split(":")[1])
		elif "." in game_time_string:
			seconds_remaining = int(game_time_string.split(".")[0])
		dt = datetime.datetime(int(date_string[:4]), int(date_string[4:6]),
									   int(date_string[6:8]), 0, 0, 0)
		dt += datetime.timedelta(minutes = QUARTER_LENGTH_IN_MIN * self.quarter)
		dt -= datetime.timedelta(minutes = minutes_remaining, seconds = seconds_remaining)
		return dt
		

Base.metadata.create_all(db)
