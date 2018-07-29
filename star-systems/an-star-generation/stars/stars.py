# -*- coding: utf-8 -*-
import math
import json
import random

# STARS
#
# star systems can be single like our solar system or double, triple etc
# includes white dwarves, neutron stars and black holes

# many calculations such as star IMF, luminosity, radius and surface temperature
# use solar constants - sometimes as as the number one to get the ratio to
# the solar constant for the given attribute
# https://en.wikipedia.org/wiki/Solar_mass
# https://en.wikipedia.org/wiki/Solar_luminosity
# https://en.wikipedia.org/wiki/Solar_radius
SOLAR_MASS = 198855 * 10**25
SOLAR_LUMINOSITY = 3828 * 10**23
SOLAR_RADIUS = 6957 * 10**5

STEFAN_BOLTZMANN_CONSTANT = 5.670373e-8

MAX_SYSTEM_STARS = "TODO"
# https://en.wikipedia.org/wiki/Stellar_classification

SPECTRAL_TYPE_O = "O"
SPECTRAL_TYPE_B = "B"
SPECTRAL_TYPE_A = "A"
SPECTRAL_TYPE_F = "F"
SPECTRAL_TYPE_G = "G"
SPECTRAL_TYPE_K = "K"
SPECTRAL_TYPE_M = "M"

# https://worldbuilding.stackexchange.com/questions/41216/starbuilding-what-is-lacking-in-the-logic-behind-cosmos-2-star-system-generatio
SPECTRAL_TYPE_O_MAX_MASS = 150
SPECTRAL_TYPE_B_MAX_MASS = 16
SPECTRAL_TYPE_A_MAX_MASS = 2.1
SPECTRAL_TYPE_F_MAX_MASS = 1.4
SPECTRAL_TYPE_G_MAX_MASS = 1.04
SPECTRAL_TYPE_K_MAX_MASS = 0.80
SPECTRAL_TYPE_M_MAX_MASS = 0.50

# https://en.wikipedia.org/wiki/Metallicity
# https://www.aanda.org/articles/aa/pdf/2011/06/aa16276-10.pdf
# 0 == metallicity of the sun
METALLICITY = 0

# https://en.wikipedia.org/wiki/Initial_mass_function
# https://github.com/Azeret/galIMF
star_IMF_dist = []
IMF_star_count = 0
def init_star_IMF_dist():
    global star_IMF_dist
    global IMF_star_count
    ranges0 = []
    ranges1 = []
    acc_prob = 0
    total_stars = 0

    f = open("stars/GalIMF_OSGIMF.txt", "r")
    lines = f.readlines()
    line = 0
    for l in lines:
        if line > 2:
            r_center, r, r_upper_limit, r_lower_limit, star_count = l.split()
            ranges0.append((float(r_upper_limit), int(star_count)))
            total_stars += int(star_count)
        line += 1

    for r in ranges0:
        prob = r[1] / float(total_stars)
        acc_prob += prob
        ranges1.append((acc_prob, r[0]))

    star_IMF_dist = ranges1
    IMF_star_count = total_stars
    return

def star_IMF(p):
    if not star_IMF_dist:
        init_star_IMF_dist()

    i = 0
    while star_IMF_dist[i][0] < p:
        i += 1

    upper = star_IMF_dist[i][1]
    lower = 0 if i == (IMF_star_count - 1) else star_IMF_dist[i+1][1]
    return lower + ((upper - lower) * random.random())

def star_spectral_type(mass_ratio):
    if mass_ratio < SPECTRAL_TYPE_M_MAX_MASS:
        return SPECTRAL_TYPE_M
    elif mass_ratio < SPECTRAL_TYPE_K_MAX_MASS:
        return SPECTRAL_TYPE_K
    elif mass_ratio < SPECTRAL_TYPE_G_MAX_MASS:
        return SPECTRAL_TYPE_G
    elif mass_ratio < SPECTRAL_TYPE_F_MAX_MASS:
        return SPECTRAL_TYPE_F
    elif mass_ratio < SPECTRAL_TYPE_A_MAX_MASS:
        return SPECTRAL_TYPE_A
    elif mass_ratio < SPECTRAL_TYPE_B_MAX_MASS:
        return SPECTRAL_TYPE_B
    elif mass_ratio < SPECTRAL_TYPE_O_MAX_MASS:
        return SPECTRAL_TYPE_O

# https://en.wikipedia.org/wiki/Mass%E2%80%93luminosity_relation
def star_luminosity(mass_ratio):
    if mass_ratio < 0.43:
        a = 2.3
        b = 0.23
    elif mass_ratio < 2:
        a = 4
        b = 1
    elif mass_ratio < 20:
        a = 3.5
        b = 1.5
    else:
        a = 1
        b = 3200

    return b * mass_ratio**a

# http://faculty.buffalostate.edu/sabatojs/courses/GES639/S10/reading/mass_luminosity.pdf
def star_radius(mass_ratio):
    if mass_ratio < 1.66:
        return 1.06*mass_ratio**0.945
    else:
        return 1.33*mass_ratio**0.555

# https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_law#Temperature_of_stars
def star_surface_temperature(luminosity, radius):
    return (luminosity / (4*math.pi*STEFAN_BOLTZMANN_CONSTANT*radius**2))**0.25

def new_star(p):
    mass_ratio   = star_IMF(p)
    stype        = star_spectral_type(mass_ratio)
    radius_ratio = star_radius(mass_ratio)
    lum_ratio    = star_luminosity(mass_ratio)
    lum          = lum_ratio    * SOLAR_LUMINOSITY
    radius       = radius_ratio * SOLAR_RADIUS

    surface_temp = star_surface_temperature(lum, radius)
    return {"solar_masses": mass_ratio,
            "spectral_type": stype,
            "lum_ratio": lum_ratio,
            "radius_ratio": radius_ratio,
            "surface_temperature": surface_temp}
