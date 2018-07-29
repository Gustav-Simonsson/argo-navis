# -*- coding: utf-8 -*-
import math
import json
import random
import csv

# PLANETS
#
# TODO: rogue planets!! :D so cool
#
# This is loosely based on these two sources:
# https://worldbuilding.stackexchange.com/questions/41216/starbuilding-what-is-lacking-in-the-logic-behind-cosmos-2-star-system-generatio
# https://en.wikipedia.org/wiki/Planetary_system#Planets
#
# TODO: this serves as a rough prototype in lieu of algorithms closer to
#       current exoplanet data.

# https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=planets

# TODO: frost line: https://arxiv.org/pdf/1207.4284.pdf

PLANET_MAX_COUNT = 12
PLANET_ROLL = 0.85

# The masses of Earth and Jupiter are commonly used in formulas as mass units.
PLANET_MASS_EARTH   = 5.97237 * 10**24
PLANET_MASS_JUPITER = 1.8982  * 10**27

def new_planets(star):
	planets = []
	#while random.random() < PLANET_ROLL and len(planets) < PLANET_MAX_COUNT:
	planets.append(new_planet(star))
	return planets

def new_planet(star):
	mass_type = new_planet_type()
	mass = new_planet_mass(mass_type)
	orbit_params = new_planet_orbit_params(star, mass)

	radii = 1.0

	gravity = 1.0

	comp_type = "desert_planet"

	magnetic_field = 1.0

	return {"mass_type": mass_type,
			"earth_masses": mass / PLANET_MASS_EARTH,
			"orbit": orbit_params,
			#"earth_radii": earth_radii,
			#"magnetic_field": magnetic_field,
			# "":,
			}


# For now, we simplify mass probabilities in a few broad categories:
# https://en.wikipedia.org/wiki/Sub-Earth
# https://en.wikipedia.org/wiki/Earth_analog
# https://en.wikipedia.org/wiki/Super-Earth
# https://en.wikipedia.org/wiki/Giant_planet
PLANET_TYPE_SUB_EARTH = "SUB_EARTH"
PLANET_TYPE_EARTH_LIKE = "EARTH_LIKE"
PLANET_TYPE_SUPER_EARTH = "SUPER_EARTH"
PLANET_TYPE_GIANT = "GIANT_PLANET"

# The mass of Ceres is a safe lower bound on planet mass, as it is
# the lowest mass body we know of that is verified to be in hydrostatic equilibrium:
# https://en.wikipedia.org/wiki/Hydrostatic_equilibrium
PLANET_MASS_MIN = 0.00015 * PLANET_MASS_EARTH

# Relatively common thresholds
PLANET_MASS_MAX_SUB_EARTH = 0.8 * PLANET_MASS_EARTH
PLANET_MASS_MAX_EARTH_LIKE = 1.9 * PLANET_MASS_EARTH
PLANET_MASS_MAX_SUPER_EARTH = 10 * PLANET_MASS_EARTH
# While debated, as safe upper bound is 13 Jupiter masses,
# as per IAU's current definition of exoplanets: https://en.wikipedia.org/wiki/Giant_planet
# There seems to be no common definition on mass thresholds for
# Ice Giants vs Gas Giants, so we define them later on from composition
PLANET_MASS_MAX_GIANT = 13 * PLANET_MASS_JUPITER

# TODO: replace uniform with proper distributions
# TODO: star mass -> max ind and total planet masses
def new_planet_mass(type):
	if type == PLANET_TYPE_SUB_EARTH:
		return random.uniform(PLANET_MASS_MIN, PLANET_MASS_MAX_SUB_EARTH)
	elif type == PLANET_TYPE_EARTH_LIKE:
		return random.uniform(PLANET_MASS_MAX_SUB_EARTH, PLANET_MASS_MAX_EARTH_LIKE)
	elif type == PLANET_TYPE_SUPER_EARTH:
		return random.uniform(PLANET_MASS_MAX_EARTH_LIKE, PLANET_MASS_MAX_SUPER_EARTH)
	else: # TODO: def not uniform up to MAX - as that's almost brown dwarf
		return random.uniform(PLANET_MASS_MAX_SUPER_EARTH, PLANET_MASS_MAX_GIANT / 4)

# TODO: these are placeholder accumulating probabilities with no scientific basis
PLANET_PROB_SUB_EARTH = 0.33
PLANET_PROB_EARTH_LIKE = 0.55
PLANET_PROB_SUPER_EARTH = 0.77
# PLANET_TYPE_GIANT = 1.0
def new_planet_type():
	r = random.random()
	if r < PLANET_PROB_SUB_EARTH:
		return PLANET_TYPE_SUB_EARTH
	elif r < PLANET_PROB_EARTH_LIKE:
		return PLANET_TYPE_EARTH_LIKE
	elif r < PLANET_PROB_SUPER_EARTH:
		return PLANET_TYPE_SUPER_EARTH
	else:
		return PLANET_TYPE_GIANT
	return

#### Keplerian Orbital Params
#
# * An apsis is an extreme point in an orbit.
# * The peri- and ap-/apo- prefixes means near and away from, respectively.
# * Examples:
#   FARTHEST      FOCUS      NEAREST
#   apoapsis      orbit      periapsis
#   apocenter	  primary    pericenter
#   aphelion      Sun        perihelion
#   apastron      star       periastron
#   apogee        Earth      perigee
#
# 1. Eccentricity:  a non-negative number denoting how elongated the orbit is compared to a circle.
#                   examples: 0 equals a circle.  0.0167 for Earth.  >=1 is an escape orbit.
#
# 2. Semimajor axis:  for a circle, this is the radius.  for an ellipse, it's half of the longest diameter.
#                     example: 1 astronomical unit (au) for Earth.
#
# 3. Inclination:  the vertical tilt of the ellipse vs the reference plane.
#                  examples: 90 degrees for a polar orbit.  0 degrees for an orbit around a planet's equator.
#
# 4. Longitude of the ascending node:  the horizontal angle of the orbit vs the direction of the reference plane;
#                                      the horizontal version of inclination.
#                                      examples: -11.26064 degrees for Earth.  0 for an orbit with 0 inclination.
#
# 5. Argument of periapsis:  the angle from the ascending node to the periapsis.
#                            examples: 114.20783 degrees for Earth.  0 if orbit is a circle.
#
# 6. True anomaly:  the angle between the current position of the orbiting object and
#                   the direcetion of the orbit periapsis, as seen from the orbited object.
#                   examples: at periapsis: 0 degrees.  at apoapsis: 180 degrees.
#
# See: https://en.wikipedia.org/wiki/Orbital_elements
#
# TODO: take into account recent exoplanet research such as:
# * https://arxiv.org/pdf/1402.7086.pdf
# * https://arxiv.org/pdf/0710.1065.pdf
#
# For now, the algorithm is:
# 1. we parse http://exoplanet.eu/catalog/all_fields/ to derive probabilities for orbital params.
# 2. current data has several observational biases: https://www.geol.umd.edu/~jmerck/geol212/lectures/30.html
#    * massive planets
#    * orbiting very close to parent star
#    * orbiting relatively small stars
#
#
# * https://arxiv.org/abs/1008.4152
# * 
# 
# To account for observational biases, we give current exoplanet data 50% weight,
# and fill in the remaining 50% using a rough extrapolating heuristic:
# * more planets with lower masses
# * more planets orbiting farther out from the parent star
#
# Moreover, we assume that planets are as common around larger stars as they are around smaller stars.
# We aim to refine all these parameters and assumptions as new exoplanet data arrives and we see
# more studies on how to account for observational biases.
# TODO: this calculates probabilities for each orbital parameter in isolation - should be tied together
#
ORBIT_PARAMS = ['mass', 'radius', 'eccentricity', 'semi_major_axis', 'inclination']
# exoplanet orbital parameters probability distributions
planet_prob_dists = {}
def new_planet_orbit_params(star, mass):
	debug_exoplanets()

	if not planet_prob_dists:
		init_planet_prob_dists()
	
	params = {}
	r = random.random()
	for p in ORBIT_PARAMS:
		params[p] = param_from_dist(p, r)
	return params

def init_planet_prob_dists():
	dict = parse_exoplanet_eu_catalog()
	for k, v in dict.items():
		planet_prob_dists[k] = list(filter(lambda x: x != '', dict[k]))
		planet_prob_dists[k].sort()
	
def param_from_dist(param, r):
	i = 0
	while (i / len(planet_prob_dists[param])) < r:
		i += 1
	
	lower = float(planet_prob_dists[param][i])
	upper = float(planet_prob_dists[param][i+1])
	return lower + (upper - lower) * random.random()
	
def parse_exoplanet_eu_catalog():
	with open('planets/exoplanet.eu_catalog.csv', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		# fields to calculate series of power laws over
		dict = {'mass': [], 'radius': [], 'eccentricity': [], 'semi_major_axis': [], 'inclination': []}
		for row in reader:
			for k, v in dict.items():
				dict[k].append(row[k])
		return dict
		
def debug_exoplanets():
	with open('planets/exoplanet.eu_catalog.csv', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		c = 0
		for row in reader:
			#f = lambda fields: 
			#if row['mass'] != '' and row['mass_error_min'] != '' and row['mass_error_max'] != '' and row['radius'] != '' and row['radius_error_min'] != '' and row['radius_error_max'] != '':
			c += 1

		print(c)