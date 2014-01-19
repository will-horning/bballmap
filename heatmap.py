from collections import defaultdict
import numpy as np
from PIL import Image, ImageFilter

PATH_TO_COURT_IMG = "static/nbagrid.bmp"
		
class Heatmap():
	
	def __init__(self, shot_rows, impath=PATH_TO_COURT_IMG, grid_d=(50,47)):
		self.im = Image.open(impath)
		self.im = self.im.crop((0,0,300,282))
		self.cell_w = self.im.size[0] / grid_d[0]
		self.cell_h = self.im.size[1] / grid_d[1]
		self.grid_d = grid_d
		self.grid_w, self.grid_h = self.grid_d
		self.shot_data = self.get_shot_data(shot_rows)
		self.spectrum = [(r, 0, 255) for r in range(256)]
		self.spectrum += [(255, 0, b) for b in range(255, -1, -1)]

	def gen_hm2(self, rdist=2, sd=1.2):
		shot_map = self.local_shot_totals.copy()
		sorted_sts = [(v, k) for k, v in self.local_shot_totals.iteritems()]
		sorted_sts.sort(key=lambda x: -x[0])
		mix = [[lambda x,y: 0.0]*self.grid_h for i in range(self.grid_w)]
		for n_shots, grid_loc in sorted_sts:
			if grid_loc in shot_map:
				x0 = grid_loc[0] * self.cell_w + (self.cell_w / 2)
				y0 = grid_loc[1] * self.cell_h + (self.cell_h / 2)
				g = self.make_gaussian(x0, y0, float(n_shots) / self.max_shots, rdist, rdist, sd)
				mix[grid_loc[0]][grid_loc[1]] = g
		im2 = Image.new("RGB", self.im.size)
		im2pa = im2.load()
		for x in xrange(self.im.size[0]):
			for y in xrange(self.im.size[1]):
				gx, gy = x / self.cell_w, y / self.cell_h
				i = int((len(self.spectrum) - 1) * mix[gx][gy](x, y))
				im2pa[x,y] = self.spectrum[i]				
		self.im = im2

	def generate_heatmap(self, rdist=3, sd=1.2):
		self.shot_totals = np.zeros(self.grid_d)
		self.shot_pcts = np.zeros(self.grid_d)
		visited = set()
		for shot_point in self.shot_data:
			x0, y0 = shot_point[1]
			g = self.make_gaussian(x0, y0, shot_point[2], rdist, rdist, sd)
			for x in xrange(x0 - rdist, x0 + rdist):
				for y in xrange(y0 - rdist, y0 + rdist):
					try:
						self.shot_totals[x,y] = max(g(x, y), self.shot_totals[x,y])
						if (x, y) in visited: self.shot_pcts[x,y] = np.mean([shot_point[0], self.shot_pcts[x,y]])
						else: self.shot_pcts[x,y] = shot_point[0]
					except IndexError: pass
					visited.add((x,y))
		self.shot_totals = self.shot_totals / max(np.nditer(self.shot_totals))
		im2 = Image.new('RGBA', self.im.size)
		pa = im2.load()
		for x in xrange(0, self.im.size[0]):
			for y in xrange(0, self.im.size[1]):
				gx, gy = x / self.cell_w, y / self.cell_h
				opacity = self.shot_totals[gx,gy]
				r, g, b = self.spectrum[int(self.shot_pcts[gx,gy] * 
					(len(self.spectrum) - 1))]
				pa[x,y] = int(r * opacity), 0, int(b * opacity), 200
		for i in range(4): im2 = im2.filter(ImageFilter.BLUR)
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
	    self.total_shots = sum([v[1] for v in m.values()])
	    self.max_shots = max([v[1] for v in m.values()])
	    self.local_shot_totals = {k: v[1] for k, v in m.iteritems()}
	    return [[float(v[0]) / v[1], list(k), float(v[1]) / self.total_shots] for k, v in m.iteritems()]
	    
	def make_gaussian(self, x0, y0, A, rho_x, rho_y, sd, theta=0):
	    a = np.cos(theta)**2 / (2*rho_x**2) + np.sin(theta)**2 / (2 * rho_y**2)
	    b = np.sin(2*theta) / (4*rho_y**2) - np.sin(2*theta) / (4 * rho_x**2)
	    c = np.sin(theta)**2 / (2*rho_x**2) + np.cos(theta)**2 / (2 * rho_y**2)
	    def f(x, y):
	        xd, yd = (x - x0), (y - y0)
	        return A * np.e**(-(a * xd**2 + 2 * b * xd * yd + c * yd**2))
	    return f
