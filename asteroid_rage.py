import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt

def initialize_solar_system(n_bodies):
    r0 = np.random.uniform(0, 1000, (n_bodies, 2)) # initial positions
    v0 = np.random.uniform(-50, 50, (n_bodies, 2))   # initial velocities
    m0 = np.random.uniform(1e-6, 1e-2, n_bodies)   # masses (in solar masses)
    # We assign player to index 0, sun to index 1, and other bodies after
    #r0 = r0 - r0[1] # star at origin
    v0 = v0 - v0[1] # heliocentricity!
    m0[1] = 1
    return r0, v0, m0

def gravity(r):
    pass

class CelestialObject(pyglet.sprite.Sprite):
    def __init__(self, image, r, **kwargs):
        self.r = r # position vector
        super().__init__(image, r[0], r[1], **kwargs)

    def update(self, r, dtheta = 0):
        self.x = r[0]
        self.y = r[1]
        self.rotation += dtheta
        self.scale = 0.1

class SolarSystem:
    def __init__(self, r, v, m):
        self.r = r
        self.v = v
        self.m = m

name = sys.argv[0].split('.')[0]

width = int(sys.argv[1])
height = int(sys.argv[2])

window = pyglet.window.Window(width, height, caption = name)

music = pyglet.resource.media('tocatta_and_fugue_in_D_minor.mp3')
music.play()

n_planets = 8 # eight planets
n_bodies = 10 # 1 sun, 1 player

r, v, m = initialize_solar_system(n_bodies)
system  = SolarSystem(r, v, m)

planets = []

img = pyglet.image.load('./saturnv.png')
all_bodies = pyglet.graphics.Batch() # draw everything at once

for i in range(n_planets):
    planets.append( CelestialObject(img, r[i+2], batch = all_bodies)) # FIX THIS

player = CelestialObject(img, r[0], batch = all_bodies)
star = CelestialObject(img, r[1], batch = all_bodies)

@window.event
def on_draw():
    window.clear()
    all_bodies.draw()

# where the actual game happens!
def update(dt):
    # Euler-Chromer for starters
    acc = 0
    system.v = system.v + dt*acc
    system.r = system.r + system.v*dt

    for j, planet in enumerate(planets):
        planet.update(system.r[j])

    star.update(system.r[0])
    player.update(system.r[1])


pyglet.clock.schedule_interval(update, 1 / 60) # schedule game update every 1/60th second

if __name__ == '__main__':
    pyglet.app.run()
