from collections import defaultdict
import numpy as np
from PIL import Image, ImageFilter

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
		
class Heatmap():
	
	def __init__(self, shot_rows, impath=PATH_TO_COURT_IMG, grid_d=(50,47)):
		self.im = Image.open(impath)
		self.im = self.im.crop((0,0,300,282))
		self.im = Image.eval(self.im, lambda x: x / 7)
		self.cell_w = self.im.size[0] / grid_d[0]
		self.cell_h = self.im.size[1] / grid_d[1]
		self.grid_d = grid_d
		self.grid_w, self.grid_h = self.grid_d
		self.shot_data = self.get_shot_data(shot_rows)
		self.spectrum = [(r, 0, 255) for r in range(256)]
		self.spectrum += [(255, 0, b) for b in range(255, -1, -1)]

	def generate_heatmap(self, rdist=2, sd=1.2):
		im2 = Image.new("RGBA", self.im.size)
		im2pa = im2.load()
		for gx, gy in self.local_shot_totals.keys():
			x0 = gx * self.cell_w + (self.cell_w / 2)
			y0 = gy * self.cell_h + (self.cell_h / 2)
			st = float(self.local_shot_totals.get((gx,gy), 0.0))
			f = self.make_gaussian(x0, y0, float(st) / self.max_shots, self.cell_w/2, self.cell_h/2, sd)
			shot_pct = self.local_shot_pcts.get((gx, gy), 0.0)
			i = int(shot_pct * (len(self.spectrum) - 1))
			r, g, b = self.spectrum[i]
			for dx in xrange(self.cell_w):
				for dy in xrange(self.cell_h):
					x = gx * self.cell_w + dx
					y = gy * self.cell_h + dy
					a = int(255 * f(x,y))
					im2pa[x,y] = r, g, b, a		
		self.im.paste(im2, (0,0), im2)

	def get_shot_data(self, shot_rows):
	    m = defaultdict(lambda: [0, 0])
	    for i in shot_rows:
	    	x1, x2 = self.grid_w / 2 + int(i[0]), self.grid_h + int(i[1])
	    	shot_made = int(i[2])
	        if x2 > self.grid_h: x1, x2 = self.grid_w - x1, 2*self.grid_h - x2
	        if x1 >= self.grid_w: x1 -= 1
	        if x2 >= self.grid_h: x2 -= 1
	        m[(x1,x2)][1] += 1
	        if shot_made: m[(x1,x2)][0] += 1
	    # self.total_shots = sum([v[1] for v in m.values()])
	    self.max_shots = max([v[1] for v in m.values()])
	    self.local_shot_totals = {k: v[1] for k, v in m.iteritems()}
	    self.local_shot_pcts = {k: float(v[0])/v[1] for k, v in m.iteritems()}
	    # return [[k, float(v[0]) / v[1], v[1]] for k, v in m.iteritems()]
	    
	def make_gaussian(self, x0, y0, A, rho_x, rho_y, sd, theta=0):
	    a = np.cos(theta)**2 / (2*rho_x**2) + np.sin(theta)**2 / (2 * rho_y**2)
	    b = np.sin(2*theta) / (4*rho_y**2) - np.sin(2*theta) / (4 * rho_x**2)
	    c = np.sin(theta)**2 / (2*rho_x**2) + np.cos(theta)**2 / (2 * rho_y**2)
	    def f(x, y):
	        xd, yd = (x - x0), (y - y0)
	        return A * np.e**(-(a * xd**2 + 2 * b * xd * yd + c * yd**2))
	    return f

	# def gen_hm3(self, rdist=2, sd=1.2):
	# 	im2 = Image.new("RGB", self.im.size)
	# 	for loc, sp, st in self.shot_data:
	# 		gim = Image.new("RGBA", (rdist * self.cell_w, rdist * self.cell_h))
	# 		pa = gim.load()
	# 		x0, y0 = gim.size[0] / 2, gim.size[1] / 2
	# 		f = self.make_gaussian(x0, y0, float(st) / self.max_shots, x0, y0, sd)
	# 		for x in xrange(gim.size[0]):
	# 			for y in xrange(gim.size[1]):
	# 				i = int(sp * (len(self.spectrum) - 1))
	# 				r, g, b = self.spectrum[i]
	# 				pa[x,y] = r, g, b, int(f(x, y) * 255)
	# 		px, py = loc[0] * self.cell_w, loc[1] * self.cell_h
	# 		im2.paste(gim, (px, py), gim)
	# 	for i in range(3): im2 = im2.filter(ImageFilter.BLUR)
	# 	im3 = Image.new("RGBA", self.im.size)
	# 	im3pa = im3.load()
	# 	for x in xrange(self.im.size[0]):
	# 		for y in xrange(self.im.size[1]):
	# 			r,g,b = im2.getpixel((x,y))
	# 			im3pa[x,y] = r,g,b,128
	# 	self.im.paste(im3, (0,0), im3)

	# def generate_heatmap(self, rdist=3, sd=1.2):
	# 	self.shot_totals = np.zeros(self.grid_d)
	# 	self.shot_pcts = np.zeros(self.grid_d)
	# 	visited = set()
	# 	for shot_point in self.shot_data:
	# 		x0, y0 = shot_point[1]
	# 		g = self.make_gaussian(x0, y0, shot_point[2], rdist, rdist, sd)
	# 		for x in xrange(x0 - rdist, x0 + rdist):
	# 			for y in xrange(y0 - rdist, y0 + rdist):
	# 				try:
	# 					self.shot_totals[x,y] = max(g(x, y), self.shot_totals[x,y])
	# 					if (x, y) in visited: self.shot_pcts[x,y] = np.mean([shot_point[0], self.shot_pcts[x,y]])
	# 					else: self.shot_pcts[x,y] = shot_point[0]
	# 				except IndexError: pass
	# 				visited.add((x,y))
	# 	self.shot_totals = self.shot_totals / max(np.nditer(self.shot_totals))
	# 	im2 = Image.new('RGBA', self.im.size)
	# 	pa = im2.load()
	# 	for x in xrange(0, self.im.size[0]):
	# 		for y in xrange(0, self.im.size[1]):
	# 			gx, gy = x / self.cell_w, y / self.cell_h
	# 			opacity = self.shot_totals[gx,gy]
	# 			r, g, b = self.spectrum[int(self.shot_pcts[gx,gy] * 
	# 				(len(self.spectrum) - 1))]
	# 			pa[x,y] = int(r * opacity), 0, int(b * opacity), 200
	# 	for i in range(4): im2 = im2.filter(ImageFilter.BLUR)
	# 	self.im.paste(im2, (0,0), im2)
