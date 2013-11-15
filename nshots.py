from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *

Session = sessionmaker()
db = create_engine("sqlite:///shots.db")
Session.configure(bind=db)
session = Session()

players = session.query(Player).all()
i = 0
for p in players:
	shots = session.query(Shot).filter_by(player_id = p.id).all()
	p.n_shots = len(shots)
	print i
	i += 1
	session.add(p)
session.commit()
session.close()
	
