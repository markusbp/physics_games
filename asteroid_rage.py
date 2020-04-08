import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt

from pyglet.window import key
import tools

G = 40

def gravity_acc(r, m):
    d = r - r[:, np.newaxis] # find all distances
    f = np.zeros((len(r), len(r)-1, 2))
    indices = np.arange(len(r))
    # calculate n body problem in inefficient manner :(
    for i in range(len(r)):
        mask = indices != i # do not include the body itself
        f[i] = G*m[mask, None]/np.linalg.norm(d[i, mask], axis = -1, keepdims = True)**3*d[i,mask]
    return np.sum(f, axis = 1)

class CelestialObject(pyglet.sprite.Sprite):
    def __init__(self, image, r0, **kwargs):
        # class for wrapping pyglet sprites so that we can work with arrays
        # image: sprite appearance, png image, r0: initial position
        super().__init__(image, r0[0], r0[1], **kwargs)

    def update(self, r, dtheta = 0):
        self.x = r[0] # update x
        self.y = r[1] # update y
        self.rotation += dtheta # optionally increment rotation

class SolarSystem:
    def __init__(self, n_bodies, width, height):
        self.n_bodies = n_bodies
        self.width = width
        self.height = height
        self.rf = 0 # select reference frame to be object 1, i.e. sun!

        r, v, m = self.initialize_system()
        self.r = r # positions
        self.v = v # velocities
        self.m = m # masses

    def update(self, dt):
        # Euler-Chromer for starters
        acc = gravity_acc(self.r, self.m)
        self.v = self.v - self.v[self.rf] + dt*acc
        self.r = self.r + self.v*dt

    def convert_to_fuel(self, id):
        # removes body no. id from arrays r,v and m, and adds its mass to player
        self.m[0] = self.m[0] + self.m[id]
        self.m = np.delete(self.m, id, axis = 0)
        self.r = np.delete(self.r, id, axis = 0)
        self.v = np.delete(self.v, id, axis = 0)

    def initialize_system(self):
        # Generate initial positions r0, velocities v0, and masses m0
        center = np.array([int(self.height/2), int(self.width/2)])
        r0 = np.random.uniform((0, 0), (self.height/2/5, self.width/2), (self.n_bodies, 2))
        r0 = np.zeros((self.n_bodies,2))
        r0[:,0] = np.linspace(0, int(self.width/2), self.n_bodies)
        v0 = np.random.uniform(-1, 1, (self.n_bodies, 2))*np.array([0,1])
        m0 = np.random.uniform(1e-6, 1e-2, self.n_bodies)   # solar masses
        # Assign player to index 0, sun to index 1, and other bodies after
        # Shift system so that star is at center of screen
        r0 = r0 - r0[self.rf] + center
        v0 = v0 - v0[self.rf] # heliocentricity, sun at rest
        m0[1] = 1 # solar masses
        return r0, v0, m0

name = sys.argv[0].split('.')[0]

width = int(sys.argv[1])
height = int(sys.argv[2])

window = pyglet.window.Window(width, height, caption = name)
#music = pyglet.resource.media('tocatta_and_fugue_in_D_minor.mp3')
#music.play()

controller = key.KeyStateHandler() # create a controller
window.push_handlers(controller) # connect controller to game window

# Load icons for solar system objects and player
background  = pyglet.image.load('./background.png')
player_icon = tools.load_sprite_image('./player.png')
planet_icon = tools.load_sprite_image('./planet.png')
star_icon = tools.load_sprite_image('./star.png')

all_bodies = pyglet.graphics.Batch() # draw everything at once

n_planets = 8 # eight planets
n_bodies = 10 # 1 sun, 1 player

# create a solar system which does calculations!
sol = SolarSystem(n_bodies, width, height)

# create player object
player = CelestialObject(player_icon, sol.r[0], batch = all_bodies)

bodies = [] # group the other bodies in a list!
# add star first, then planets
bodies.append(CelestialObject(star_icon, sol.r[1], batch = all_bodies))
for i in range(n_planets):
    bodies.append(CelestialObject(planet_icon, sol.r[i+2], batch = all_bodies))

eating_distance = 40

@window.event
def on_draw():
    window.clear()
    background.blit(0,0)
    all_bodies.draw()

# where the actual game happens!

dv = 0.05
dtheta = 1
def update(dt):

    sol.update(dt*20) # update solar system
    # update the sprites accordingly
    for j, body in enumerate(bodies):
        body.update(sol.r[j+1])
    player.update(sol.r[0])

    # Check if any object is close enough to be converted to fuel
    dist_to_player = np.linalg.norm(sol.r[0] - sol.r[1:], axis = 1)
    close_enough = dist_to_player < eating_distance

    if np.any(close_enough):
        object_id = np.argmin(dist_to_player)
        bodies[object_id].delete() # remove sprite
        del(bodies[object_id]) # and list entry
        sol.convert_to_fuel(object_id + 1) # and remove object from calculations

    if controller[key.W]:
        orientation = np.radians(player.rotation)
        boost = np.array([np.sin(orientation), np.cos(orientation)])*dv
        sol.v[0] = sol.v[0] + boost
    if controller[key.E]:
        player.rotation += dtheta
        player.rotation = tools.bound_angles(player.rotation)
        print(player.rotation)
    if controller[key.Q]:
        player.rotation -= dtheta
        player.rotation = tools.bound_angles(player.rotation)
        print(player.rotation)

pyglet.clock.schedule_interval(update, 1 / 60) # schedule game update every 1/60th second

if __name__ == '__main__':
    pyglet.app.run()
