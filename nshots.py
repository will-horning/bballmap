"""
This script is for tallying up the number of shots a player has, so the ones
with statiscally insignificant playing time can be filtered out quickly.
Only needs to be run once with db update.
"""

from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *

Session = sessionmaker()
db = create_engine("sqlite:///shots.db")
Session.configure(bind=db)
session = Session()

players = session.query(Player).all()
for p in players:
	shots = session.query(Shot).filter_by(player_id = p.id).all()
	p.n_shots = len(shots)
	session.add(p)
session.commit()
session.close()
	
