from collections import defaultdict
import numpy as np
from PIL import Image, ImageFilter
import math
# PATH_TO_COURT_IMG = "static/nbagrid.bmp"
PATH_TO_COURT_IMG = "static/nbacourt2.png"
		
class Heatmap():
	def __init__(self, shot_rows, impath=PATH_TO_COURT_IMG, grid_d=(50,47)):
		self.im = Image.open(impath)
		# self.im = Image.eval(self.im, lambda x: x / 8)
		self.cell_w = self.im.size[0] / grid_d[0]
		self.cell_h = self.im.size[1] / grid_d[1]
		self.grid_d = grid_d
		self.grid_w, self.grid_h = self.grid_d
		self.shot_data = self.get_shot_data(shot_rows)
		self.spectrum = [(r, 0, 255) for r in range(256)]
		self.spectrum += [(255, 0, b) for b in range(255, -1, -1)]
		self.shot_rows = shot_rows
		
	def k_nearest_gen(self, rdist=2, sd=1.2):
		srim = self.get_shooting_rate_map(rdist=rdist, sd=sd)
		spim = self.get_shooting_pct_map()
		self.im.paste(spim, (0,0), srim)

	def get_shooting_pct_map(self):
		shot_pct_im = Image.new("RGB", self.im.size)
		shot_pct_pa = shot_pct_im.load()
		for gx in xrange(self.grid_w):
			for gy in xrange(self.grid_h):
				sp = self.local_shot_pcts.get((gx, gy), self.k_nearest_shot_pct(gx, gy))
				for px, py in self.cell_pixel_coords(gx, gy):
					i = int(sp * (len(self.spectrum) - 1))
					shot_pct_pa[px,py] = self.spectrum[i]
		return shot_pct_im

	def cell_pixel_coords(self, gx, gy):
		for px in xrange(gx * self.cell_w, (gx + 1) * self.cell_w):
			for py in xrange(gy * self.cell_h, (gy + 1) * self.cell_h):
				yield (px, py)
 
	def grid_neighbors(self, gx0, gy0, rdist):
		for gx in xrange(-rdist + gx0, rdist + gx0):
			for gy in xrange(-rdist + gy0, rdist + gy0):
				if gx < self.grid_w and gy < self.grid_h and gx >= 0 and gy >= 0:
					yield (gx, gy)

	def get_shooting_rate_map(self, rdist=2, sd=1.2):
		shot_rate_im = Image.new('L', self.im.size)
		shot_rate_pa = shot_rate_im.load()
		for (gx, gy), st in self.local_shot_totals.copy().iteritems():
			x0 = gx * self.cell_w + (self.cell_w / 2)
			y0 = gy * self.cell_h + (self.cell_h / 2)
			w, h = rdist * self.cell_w, rdist * self.cell_h
			f = self.make_gaussian(x0, y0, float(st), w, h, sd)
			for gx1, gy1 in self.grid_neighbors(gx, gy, rdist):
				px, py = (gx + 0.5) * self.cell_w, (gy + 0.5) * self.cell_h
				self.local_shot_totals[gx,gy] += f(px, py)
		shot_max = max(self.local_shot_totals.values())
		for gx in xrange(self.grid_w):
			for gy in xrange(self.grid_h):
				for px, py in self.cell_pixel_coords(gx, gy):
					shot_rate = self.local_shot_totals.get((gx,gy), 0.0)
					shot_rate /= float(shot_max)
					try: shot_rate_pa[px,py] = int(255.0 * shot_rate)
					except IndexError: pass
		return shot_rate_im

	def k_nearest_shot_pct(self, gx, gy):
		dist = lambda x, y: math.sqrt((gx - x)**2 + (gy - y)**2)
		_, mx, my = min([(dist(x, y), x, y) for x, y in self.local_shot_pcts.keys()])
		return self.local_shot_pcts[mx, my]

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
		self.max_shots = max([v[1] for v in m.values()])
		self.local_shot_totals = {k: v[1] for k, v in m.iteritems()}
		self.local_shot_pcts = {k: float(v[0])/v[1] for k, v in m.iteritems()}
		
	def make_gaussian(self, x0, y0, A, rho_x, rho_y, sd, theta=0):
		a = np.cos(theta)**2 / (2*rho_x**2) + np.sin(theta)**2 / (2 * rho_y**2)
		b = np.sin(2*theta) / (4*rho_y**2) - np.sin(2*theta) / (4 * rho_x**2)
		c = np.sin(theta)**2 / (2*rho_x**2) + np.cos(theta)**2 / (2 * rho_y**2)
		def f(x, y):
			xd, yd = (x - x0), (y - y0)
			return A * np.e**(-(a * xd**2 + 2 * b * xd * yd + c * yd**2))
		return f

	def gaussian_saturation(self, val, dist, r_dist):
		self.c = 1.5
		if val == 0: return 0.0
		a = val
		b = 0
		c = self.c
		x = dist
		return a * pow(math.e, (-1 * pow((x - b), 2) / (2 * c * c)))

	def old_gen_hm(self, rdist=3):
		m = defaultdict(lambda: [0, 0])
		for i in self.shot_rows:
			x1, x2 = self.grid_w / 2 + int(i[0]), self.grid_h + int(i[1])
			shot_made = int(i[2])
			if x2 > self.grid_h: x1, x2 = self.grid_w - x1, 2*self.grid_h - x2
			if x1 >= self.grid_w: x1 -= 1
			if x2 >= self.grid_h: x2 -= 1
			if shot_made: m[(x1,x2)][1] += 1
			else: m[(x1,x2)][0] += 1
		m2 = m.copy()
		for (gx, gy), v in m2.iteritems():
			for gi in xrange(gx - rdist, gx + rdist + 1):
				for gj in xrange(gy - rdist, gy + rdist + 1):
					dist = math.sqrt((gx - gi)**2 + (gy - gj)**2)
					r_val = [self.gaussian_saturation(v[0], dist, rdist),
							self.gaussian_saturation(v[1], dist, rdist)]
					prev = m.get((gi,gj), (0,0))
					m[(gi,gj)] = [prev[0] + r_val[0],
								  prev[1] + r_val[1]]
		miss_min = min([v[0] for v in m.values()])
		miss_max = max([v[0] for v in m.values()])
		made_min = min([v[1] for v in m.values()])
		made_max = max([v[1] for v in m.values()])
		print miss_min, miss_max, made_min, made_max
		for (gx, gy), v in m.iteritems():
			v[0] = (float(v[0]) - miss_min) / (miss_max - miss_min)
			v[1] = (float(v[1]) - made_min) / (made_max - made_min)
		impa = self.im.load()
		for x in xrange(self.im.size[0]):
			for y in xrange(self.im.size[1]):
				gx, gy = x / self.cell_w, y / self.cell_h
				if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
					r = 255 * m.get((gx,gy), [0,0])[1]
					b = 255 * m.get((gx,gy), [0,0])[0]
					r1, g1, b1, a1 = impa[x,y]
					impa[x,y] = int(r1/4 + r), int(g1/4), int(b1/4 + b), a1
