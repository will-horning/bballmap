from math import sqrt
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


def permute_combos(*args):
    """
    Given multiple lists (at least 2), will generate
    every possible series of single element selections
    from those lists (in the order theyre given as arguments).
    e.g. permute_combos([1,2], [3,4]) => [1,3], [1,4], [2,3], [2,4]
    """
    if len(args) <= 1:
        raise Exception("permute_combos takes at least two lists")
    if len(args) == 2:
        for a in args[0]:
            for b in args[1]:
                yield [a, b]
    else:
        for combo in permute_combos(*args[:-1]):
            for a in args[-1]: yield combo + [a]


def get_matrix_val(mat, rsize, rnum, cnum):
	return mat[(rsize*rnum) + cnum]

def convert2d_to_1d(twodlist):
	onedlist = []
	for x in range(len(twodlist)):
		for y in range(len(twodlist[0])):
			onedlist.append(twodlist[x][y])
	return onedlist

def group_by_opposing_team(player):
    games = {}
    for s in player.shots:
        teams = s.game_teams.split(",")
        team = teams[0]
        if player.team.name in team: team = teams[1]
        team = "".join([c for c in team if c.isalnum() or c.isspace()]).strip()
        if team in games.keys(): games[team].append(s)
        else: games[team] = [s]
    return games


def remove_free_throws(shots):
    return [so for so in shots if int(so.shot_type) not in range(10,19)]


def standard_deviation(vals):
	diffs = []
	for i in len(vals) - 1:
		diffs.append(abs(vals[i+1] - vals[i]))
	return float(sum(diffs)) / len(vals)

def normal_distribution(vals):
	mean = float(sum([sum(v[:2]) for v in vals])) / len(vals)
	sd = float(sum([abs(sum(v[:2]) - mean) for v in vals])) / len(vals)
	return mean, sd

		
def get_session():
	Session = sessionmaker()
	db = create_engine("mysql://root:zoopzoop@localhost/balladb")
	Session.configure(bind=db)
	return Session()

def cluster(a, k):
	ret = []
	i = 0
	while i < len(a):
		clust = []
		for j in range(k): clust.append(a[j+i])
		ret.append(clust)
		i += k
	return ret

def distance(a, b):
	dx = b[0] - a[0]
	dy = b[1] - a[1]
	return sqrt((dx * dx) + (dy * dy))

def in_bounds(loc, dim):
	return loc[0] < dim[0] and loc[0] >= 0 and loc[1] < dim[1] and loc[1] >= 0

def histogram(m):
	h = {}
	if type(m) == dict:
		for k, v in m.iteritems():
			if v in h.keys():
				h[v] += 1
			else:
				h[v] = 1
	else:
		for v in m:
			if v in h.keys():
				h[v] += 1
			else:
				h[v] = 1
	return h

def sani(s):
    snew = []
    for c in s:
	    if c.isalnum():
		    snew.append(c)
	    else:
		    snew.append("_")
    return "".join(snew)

def flatten(a):
	ret = []
	for i in a:
		if type(i) is list:
			ret += flatten(i)
		else:
			ret.append(i)
	return ret

# def loose_map(mapfun, *args):
# 	for a in args:
# 		if type(a) is list:
# 			a = map(mapfun, a)
# 		elif type(m1) is dict:
# 			for k,v in dict.iteritems():


def add_sresults(cs):
	for coord in cs:
		i = random.randint(0,10)
		if i < 3: coord.append("1")
		else: coord.append("0")
