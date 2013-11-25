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
	print p
	n_freethrows = 0
	shots = session.query(Shot).filter_by(player_id = p.id).order_by(Shot.datetime).all()
	if len(shots) < 400: continue
	for i, shot in enumerate(shots[1:-2]):
		prev_shot = shots[i-1]
		next_shot = shots[i+1]
		if prev_shot.datetime == shot.datetime:
			print prev_shot.datetime
			print shot.datetime
			n_freethrows += 1
			session.add(shot)
			session.add(prev_shot)
			shot.shot_type = "Free Throw"
			prev_shot.shot_type = "Free Throw"
   	print n_freethrows
	print len(shots)
session.commit()
session.close()


		
