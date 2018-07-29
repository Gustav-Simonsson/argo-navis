# -*- coding: utf-8 -*-
import json
import random

import planets.planets as planets
import stars.stars as stars

#
# alpha version - stars, planets and moons.
# no neutron stars, black holes or other exotic objects.
#

#print "===="
#print "==== Argo Navis Star System Generation"
#print "==== v0.1"
#print "===="

prob = random.random()
star = stars.new_star(prob)
planets = planets.new_planets(star)
systems = [{"star": star, "planets": planets}]

world = {"star-systems": systems}
print(json.dumps(world, indent=4, sort_keys=True))
