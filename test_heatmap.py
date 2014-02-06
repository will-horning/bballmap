"""
A couple of methods for testing the runtime of a given heatmap function and
the squared error of the result.
"""
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import *
from heatmap import Heatmap
from time import time
import random
import numpy as np

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
Session = sessionmaker()
db = create_engine("sqlite:///shots.db", connect_args={'check_same_thread':False})
Session.configure(bind=db)
session = Session()

def free_throw_filter(shot_rows):
    filtered_shot_rows = []
    for shot_row in shot_rows:
        if not (shot_row[0] == 0 and abs(shot_row[1]) in [28,42]) and ("Free" not in shot_row[3] and "Lay" not in shot_row[3]):
            filtered_shot_rows.append(shot_row)
    return filtered_shot_rows

def all_coords(im):
    for x in xrange(im.size[0]):
        for y in xrange(im.size[1]):
            yield (x, y)

def avg_pixel_diff(im1, im2):
    if im1.size != im2.size or im1.format != im2.format:
        raise Exception("Images to compare must have same size and format.")
    diff_im = Image.new("L", im1.size)
    diff_im_pa = diff_im.load()
    im1pa, im2pa = im1.load(), im2.load()
    for x, y in all_coords(im1):
        p1, p2 = np.mean(im1pa[x,y]), np.mean(im2pa[x,y])
        diff_im_pa[x,y] = abs(p2 - p1)
    mean = sum([diff_im_pa[x,y] for x, y in all_coords(diff_im)])
    mean /= float(diff_im.size[0] * diff_im.size[1])
    return diff_im, mean

def compare_heatmap_gens(hm, gens):#, params):
    m = {}
    # for gen, args in izip(gens, params):
    for gen in gens:
        t1 = time()
        gen(hm) #, *args)
        t2 = time()
        m[gen] = t2 - t1
    return m

# pil = 6496
# q =  "select xcoord, ycoord, shotresult, " + \
#     " shot_type from shots where player_id = " + str(pil) + ";" 
# sqlresponse = session.execute(q)
# shot_rows = [list(row) for row in sqlresponse.fetchall()]
# filtered_shot_rows = free_throw_filter(shot_rows)
# from PIL import Image

# pct_test = 0.2
# n_test = len(filtered_shot_rows) * pct_test
# Xtest = []
# while len(Xtest) < n_test: 
#     i = random.randint(0, len(filtered_shot_rows) - 1)
#     Xtest.append(filtered_shot_rows.pop(i))



# hm = Heatmap(filtered_shot_rows)
# hm_test = Heatmap(Xtest)
# hm.k_nearest_gen()
# hm_test.k_nearest_gen()
# r = avg_pixel_diff(hm.im, hm_test.im)
# # hm.im.save("foo.png")
