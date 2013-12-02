#import radiator
import math, random
from PIL import Image
from time import time
from models import *

class HeatMap():
	def __init__(self, raw_shot_rows, impath, grid_w=50, grid_h=94):
		self.im = Image.open(impath)
		self.grid_w = grid_w
		self.grid_h = grid_h
		self.grid_coords = self.extract_coords(raw_shot_rows)
		self.cell_w = int(round(float(self.im.size[0]) / float(self.grid_w)))
		self.cell_h = int(round(float(self.im.size[1]) / float(self.grid_h)))


	def in_bounds(self, loc, dim):
		return loc[0] < dim[0] and loc[0] >= 0 and loc[1] < dim[1] and loc[1] >= 0

	def extract_coords(self, raw_shot_rows):
		"""
		Converts the raw coordinates (using CBSSports coordinate system)
		to simple x,y coordinates where the top left corner is the origin
		and x and y values are in grid cell numbers (so the max values are
		given by self.grid_w and self.grid_h).
		"""
		tls = []
		for shot_row in raw_shot_rows:
			left = 0
			top = 0
			left = ((self.grid_w / 2) + int(shot_row[0]))
			top = ((self.grid_h / 2) + int(shot_row[1]))
			if left >= self.grid_w: left = self.grid_w - 1
			if top >= self.grid_h: top = self.grid_h - 1
			tls.append([left, top, shot_row[2]])
		return tls

	def set_grid_size(self, new_dim):
		"""
		Updates the values for self.grid_coords to reflect new grid
		dimensions.
		"""
		coords = self.grid_coords
		old_dim = (self.grid_w, self.grid_h)
		old_cell_dim = (self.im.size[0] / old_dim[0],
						self.im.size[1] / old_dim[1])
		new_cell_dim = (self.im.size[0] / new_dim[0],
						self.im.size[1] / new_dim[1])
		new_coords = []
		for coord in coords:
			pixel_coord = (old_cell_dim[0] * coord[0],
						   old_cell_dim[1] * coord[1])
			new_coords.append((int(round(float(pixel_coord[0]) / new_cell_dim[0])),
							   int(round(float(pixel_coord[1]) / new_cell_dim[1])),
							   coord[2]))
		self.cell_w, self.cell_h = new_cell_dim
		self.grid_w, self.grid_h = new_dim
		self.grid_coords = new_coords

	def halve_court(self):
		"""
		Flips any locations below the half court line up to the
		top half.
		"""
		locs = self.shot_locs.copy()
		for loc, v in locs.iteritems():
			if loc[1] >= (self.grid_h / 2):
				self.shot_locs.pop(loc)
				nloc = (self.grid_w - loc[0], self.grid_h - loc[1])
				try:
					pv = self.shot_locs[nloc]
					self.shot_locs[nloc] =  [pv[0] + v[0], pv[1] + v[1]]
				except:
					self.shot_locs[nloc] = v

	def update_extrema(self):
		"""
		Checks every entry in shot_locs and sets the following
		variables to whatever the current extrema are.
		"""
		self.miss_max = max([v[0] for v in self.shot_locs.values()])
		self.made_max = max([v[1] for v in self.shot_locs.values()])
		self.total_max = max([sum(v) for v in self.shot_locs.values()])
		self.miss_min = min([v[0] for v in self.shot_locs.values()])
		self.made_min = min([v[1] for v in self.shot_locs.values()])
		self.total_min = min([sum(v) for v in self.shot_locs.values()])
		self.shot_range = self.made_max + self.miss_max
		self.diff_max = max([v[1] - v[0] for v in self.shot_locs.values()])
		self.diff_min = min([v[1] - v[0] for v in self.shot_locs.values()])
		self.diff_range = self.diff_max - self.diff_min
			

	def tally_shot_locs(self):
		"""
		Sums all the made and missed shots taken at each location
		in grid_coords, then creates a dict self.shot_locs, keys
		are 2tuple locations, values are lists with the following format:
		shot_locs[loc] = [num_made_from_loc, num_missed_from_loc]
		"""
		self.shot_locs = {}
		for shot in self.grid_coords:
			shot_result = int(shot[2])
			loc = (shot[0], shot[1])
			try:
				self.shot_locs[loc][shot_result] += 1
			except KeyError:
				self.shot_locs[loc] = [0,0]
				self.shot_locs[loc][shot_result] += 1

	def remove_outliers(self, upper_bound):
		"""
		Filters self.shot_locs based on an upperbound for the
		total number of shots.  Returns each key,val pair that
		was removed.
		"""
		removed = []
		for k, v in self.shot_locs.iteritems():
			if sum(v[:2]) > upper_bound:
				removed.append((k,v))
		for k, v in removed:
			self.shot_locs.pop(k)
		return removed
	
	def non_zero_shot_locs(self):
		return [v for v in self.shot_locs.values() if sum(v[:2]) > 0] 

	def write_grid(self, grid_color=(0,0,0)):
		p = 0
		while p < self.im.size[0]:
			for q in range(0,self.im.size[1]):
				self.im.putpixel((p,q), grid_color)
			p += self.cell_w
		q = 0
		while q < self.im.size[1]:
			for p in range(0, self.im.size[0]):
				try:
					self.im.putpixel((p, q), grid_color)
				except IndexError:
					break
			q += self.cell_h

##
##class C_HeatMap(HeatMap):
##	def generate_heatmap_image(self, grid_w=50, grid_h=94, halvecourt=True, rdist=8, sd=2.5):
##		self.set_grid_size((grid_w,grid_h))
##		self.tally_shot_locs()
##		self.remove_outliers(100)
##		if halvecourt: self.halve_court()
##		self.rad_and_shad(rdist, sd) 
##		self.im.putdata(self.pxs)
##		
##	def format_shot_locs_for_C(self):
##		made_flat = []
##		missed_flat = []
##		locs = []
##		for k,v in self.shot_locs.iteritems():
##			missed_flat.append(v[0])
##			made_flat.append(v[1])
##			locs.append(k)
##		return missed_flat, made_flat, locs
##
##	def rad_and_shad(self, r_dist=5, sd=2.5):
##		missed, made, locs = self.format_shot_locs_for_C()
##		values = list(self.im.getdata())
##		self.pxs = radiator.qwikrad(missed, made, locs, r_dist,
##									self.grid_w, self.grid_h, values,
##									self.im.size[0], self.im.size[1], sd)
##	

class Py_HeatMap(HeatMap):

	def generate_heatmap_image(self, **kwargs):
		self.set_grid_size((50,94))
		self.tally_shot_locs()
		self.remove_outliers(100)
		self.halve_court()
		self.py_radiate(**kwargs)
		self.update_extrema()
		self.find_colors2()
		self.shade_all()


	def linear_saturation(self, val, dist, r_dist, s=0.15):
		return int(round(float(val) * ((1 - (s * dist)) * val)))

	def logarithm_saturation(self, val, dist, r_dist):
		if dist <= 0: return val
		return int(round(float(val) * (1.0 - math.log(dist, r_dist))))

	def reverse_log_saturation(self, val, dist, r_dist):
		if dist >= r_dist: return 0.0
		return int(round(float(val) * (math.log(r_dist - dist, r_dist))))

	def polynomial_saturation(self, val, dist, r_dist, exp=8):
		sat = 1.0 - pow(float(dist)/r_dist,2)
		if sat < 0: sat = 0
		return val * sat

	def gaussian_saturation(self, val, dist, r_dist):
		self.c = 1.5
		if val == 0: return 0.0
		a = val
		b = 0
		c = self.c
		x = dist
		return a * pow(math.e, (-1 * pow((x - b), 2) / (2 * c * c)))

	def cauchy_saturation(self, val, dist, r_dist):
		if dist == 0: return val
		if val == 0: return 0.0
		x0 = 0
		x = dist
		#g = 1.0 / (math.pi * val)
		g = 3.0
		amp = 1.0 / (math.pi / 2.0)
		r = ((1 / math.pi) * g / (pow(x - x0,2) + (g*g))) / amp
		return r * val

		
	def get_saturation_value(self, nmade, nmiss):
		"""
		Saturation is determined by the total number of
		shots attempted at a location (made and missed),
		relative to the maximum total out of all locations.
		Returns a float in the range [0,1].
		"""
		total = nmade + nmiss
		if total == 0: return 0.05
		min_sat = 0.1
		per = float(total) / self.total_max
		sat = min_sat + ((1.0 - min_sat) * per)
		return sat

	def find_colors(self):
		"""
		Creates the 3tuple rgb value for each entry in shot_locs,
		then stores it in the dict self.loc_colors. 
		"""
		self.loc_colors = {}
		for loc, shot_count in self.shot_locs.iteritems():
			nmiss = shot_count[0]
			nmade = shot_count[1]
			hue = self.get_color(nmade - nmiss)
			sat = self.get_saturation_value(nmade, nmiss)
			self.loc_colors[loc] = tuple([int(round(h * sat)) for h in hue])

	def find_colors2(self):
		"""
		Creates the 3tuple rgb value for each entry in shot_locs,
		then stores it in the dict self.loc_colors. 
		"""
		self.loc_colors = {}
		for loc, shot_count in self.shot_locs.iteritems():
			nmiss = shot_count[0]
			nmade = shot_count[1]
			miss_p = (float(nmiss) - self.miss_min) / (self.miss_max - self.miss_min)
			made_p = (float(nmade) - self.made_min) / (self.made_max - self.made_min)
			r = int(round(255*made_p))
			b = int(round(255*miss_p))
			self.loc_colors[loc] = (r,0,b)

				
				
	def find_colors_test(self):
		self.loc_colors = {}
		for loc, shot_count in self.shot_locs.iteritems():
			nmiss = shot_count[0]
			nmade = shot_count[1]
			if (nmiss + nmade) == 0: continue
			sp = float(nmade) / (nmiss + nmade)
			if sp < 0.5: r, b = int(round(255*2*sp)), 255
			else: b, r = int(round(255*2*sp)), 255
			self.loc_colors[loc] = (r,0,b)

	def py_radiate(self, r_dist=5):
		locs = self.shot_locs.copy()
		for loc, vals in locs.iteritems():
			r_locs = []
			for x in range(-r_dist, r_dist+1):
				for y in range(-r_dist,r_dist+1):
					r_locs.append((loc[0] + x, loc[1] + y))
			for cell in r_locs:
				dist = max([abs(cell[0] - loc[0]), abs(cell[1] - loc[1])])
				r_val = [self.gaussian_saturation(vals[0], dist, r_dist),
						 self.gaussian_saturation(vals[1], dist, r_dist)]
				if all([(cell[0] < self.grid_w), (cell[1] < self.grid_h),
						(cell[0] >= 0),(cell[1] >= 0)]):
					try:
						prev = self.shot_locs[cell]
						self.shot_locs[cell] = [prev[0] + r_val[0],
												prev[1] + r_val[1]]
					except KeyError:
						self.shot_locs[cell] = r_val


	def shade_grid_cell(self, loc, rgb, opacity=0.8):
		for y in range(self.cell_h):
			for x in range(self.cell_w):
				cloc = ((self.cell_w * loc[0]) + x, (self.cell_h * loc[1]) + y)
				if self.in_bounds(cloc, self.im.size):
					pix = self.im.getpixel(cloc)
					new_rgb = list(pix)
					for i in range(3):
						new_rgb[i] /= 4
						new_rgb[i] += int(rgb[i] * opacity)
					self.im.putpixel(cloc, tuple(new_rgb))

	def shade_all(self):
		for y in range(self.grid_h):
			for x in range(self.grid_w):
				try:
					color = self.loc_colors[(x,y)]
					self.shade_grid_cell((x,y), color)
				except KeyError:
					self.shade_grid_cell((x,y), (13,0,9))

	def shade_grid_cell2(self, loc, rgb, pixels, opacity=0.8):
		for x in range(self.cell_w):
			for y in range(self.cell_h):
				cloc = ((self.cell_w * loc[0]) + x, (self.cell_h * loc[1]) + y)
				if self.in_bounds(cloc, self.im.size):
					index = ((self.im.size[0] * cloc[1]) + cloc[0])
					pix = pixels[index]
					new_rgb = list(pix)
					for i in range(3):
						new_rgb[i] /= 4
						new_rgb[i] += int(round(rgb[i] * opacity))
					pixels[index] = tuple(new_rgb)
					
	def fill_out(self):
		all_locs = []
		for x in range(self.grid_w):
			for y in range(self.grid_h):
				loc = (x,y)
				if loc not in self.shot_locs.keys():
					self.shot_locs[loc] = [0, 0]
				if len(self.shot_locs[loc]) == 0:
					self.shot_locs[loc] = [0, 0]

	def get_color(self, val):
		nval = val - self.diff_min
		i = int(round(len(self.spectrum) * (float(nval) / self.diff_range)))
		if i < 0: return self.spectrum[0]
		elif i >= len(self.spectrum): return self.spectrum[-1]
		else: return self.spectrum[i]

	def generate_spectrum(self):
		self.spectrum = []
		rr = range(0,256)
		rr.reverse()
		for r in range(0,256):
			self.spectrum.append((r,0,255))
		for b in rr:
			self.spectrum.append((255,0,b))

	def use_full_spectrum(self):
		self.spectrum = []
		rr = range(0,256)
		rr.reverse()
		for g in range(0,256):
			self.spectrum.append((255,g,0))
		for r in rr:
			self.spectrum.append((r,255,0))
		for b in range(0,256):
			self.spectrum.append((0,255,b))
		for g in rr:
			self.spectrum.append((0,g,255))
		for r in range(0,256):
			self.spectrum.append((r,0,255))
		self.spectrum.reverse()
		
	def use_duke_spectrum(self):
		self.spectrum = []
		rr = range(0,256)
		rr.reverse()
		for r in range(0,256):
			self.spectrum.append((r,r,255))
		return
		for b in rr:
			self.spectrum.append((255,0,b))

	def write_spectrum(self):
		for x in range(self.im.size[0]):
			i = int(round(float(x * len(self.spectrum)) / 300))
			for y in range(270,300):
				self.im.putpixel((x,y), self.spectrum[i])

	def shade_all2(self):
		pixels = list(self.im.getdata())
		for x in range(self.grid_w):
			for y in range(self.grid_h):
				try:
					color = self.loc_colors[(x,y)]
					self.shade_grid_cell2((x,y), color, pixels)
				except KeyError:
					self.shade_grid_cell2((x,y), (13,0,9), pixels)
		self.im.putdata(pixels)
		

	def write_spectrum2(self):
		for x in range(250):
			for y in range(282,532):
				r = 255 * (float(x) / 250)
				b = 255 * (float(y-282) / 250)
				self.im.putpixel((x,y), (r,0,b))

		
