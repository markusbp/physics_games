import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt
from pyglet.window import key

import tools
from solar_system import SolarSystem

class ScreenTransform:
    def __init__(self, width, height, system_size, zoom = 1):
        # class for transforming from physical to screen representation
        self.width = width
        self.height = height
        self.system_size = system_size
        self._zoom = zoom # optional zoom level

        self.center = np.array([int(width/2), int(height/2)])
        self.scale = self.height/(2*self.system_size)*self._zoom

    def transform(self, coord):
        # shift coord from [-bound, bound] to [height, width]*scale
        return coord*self.scale + self.center

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        self._zoom = zoom
        self.scale = self.height/(2*self.system_size)*self._zoom

class CelestialObject(pyglet.sprite.Sprite):
    def __init__(self, image, r0, **kwargs):
        # class for wrapping pyglet sprites so that we can work with arrays
        # image: sprite appearance, png image, r0: initial position
        super().__init__(image, r0[0], r0[1], **kwargs)

    def update(self, r, dtheta = 0):
        self.x = r[0] # update x
        self.y = r[1] # update y
        self.rotation += dtheta # optionally increment rotation

name = sys.argv[0].split('.')[0]

SYSTEM_SIZE = 30 # AU

width = int(sys.argv[1]) # width
height = int(sys.argv[2]) # height
window = pyglet.window.Window(width, height, caption = name)
music = pyglet.resource.media('tocatta_and_fugue_in_D_minor.mp3')
music.play()

controller = key.KeyStateHandler() # create a controller
window.push_handlers(controller) # connect controller to game window

# Load icons for solar system objects and player
background  = pyglet.image.load('./background.png')
player_icon = tools.load_sprite_image('./player.png')
planet_icon = tools.load_sprite_image('./planet.png')
star_icon = tools.load_sprite_image('./star.png')

all_bodies = pyglet.graphics.Batch() # draw everything at once in a Batch

n_planets = 8 # eight planets
n_bodies = 2 + n_planets # 1 sun, 1 player

# create a solar system which does calculations!
sol = SolarSystem(n_bodies, 1, SYSTEM_SIZE)
to_screen = ScreenTransform(width, height, SYSTEM_SIZE, 1)

# create player object
player = CelestialObject(player_icon, sol.r[0], batch = all_bodies)

bodies = [] # group the other bodies in a list!
# add star first, then planets
bodies.append(CelestialObject(star_icon, sol.r[1], batch = all_bodies))
for i in range(n_planets):
    bodies.append(CelestialObject(planet_icon, sol.r[i+2], batch = all_bodies))

@window.event
def on_draw():
    window.clear()
    background.blit(0,0) # blit happens
    all_bodies.draw()

dv = 5e-2 # boost level: fake; to be replaced with momentum exchange
dtheta = 1 # gyroscopic rotation, in degrees
eating_distance = 1

def update(dt):
    # this is where we update the window, and the game actually happens
    sol.update(dt) # update solar system motions
    # then shift from solar system coordinates to screen coordinates
    shifted = to_screen.transform(sol.r)
    # update the sprites accordingly

    for j, body in enumerate(bodies):
        body.update(shifted[j+1])
    player.update(shifted[0])

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
        boost = tools.unit_vector(orientation)*dv
        sol.v[0] = sol.v[0] + boost
    if controller[key.E]:
        player.rotation += dtheta
        player.rotation = tools.bound_angles(player.rotation)
    if controller[key.Q]:
        player.rotation -= dtheta
        player.rotation = tools.bound_angles(player.rotation)

    # zoom functionality
    if controller[key.O]:
        to_screen.zoom /= 1.1
    if controller[key.P]:
        to_screen.zoom *= 1.1

    #print(f'{to_screen.zoom}')
pyglet.clock.schedule_interval(update, 1 / 60.0) # schedule game update every 1/60th second

if __name__ == '__main__':
    pyglet.app.run()
