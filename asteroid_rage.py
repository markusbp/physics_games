import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt
from pyglet.window import key # controller

import tools
from solar_system import SolarSystem

class ScreenTransform:
    def __init__(self, width, height, system_size, zoom = 1):
        '''
        Handles transform from physical coordinates to screen coordinates
        width: screen width
        height: screen height
        system_size: scale of solar system in AU
        zoom: zoom factor; allows us to change scale
        '''
        self.width = width
        self.height = height
        self.system_size = system_size # solar system scale
        self._zoom = zoom # optional zoom level

        # center of screen
        self.center = np.array([int(width/2), int(height/2)])
        self.scale = self.height/(2*self.system_size)*self._zoom

    def transform(self, coord):
        # shift coord from [-system size, system size] to [height, width]*zoom
        return coord*self.scale + self.center

    @property
    def zoom(self):
        # set zoom: @property allows us to use a setter
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        # setter allows us to change scale factor correctly when zoom changes
        self._zoom = zoom
        self.scale = self.height/(2*self.system_size)*self._zoom

class CelestialObject(pyglet.sprite.Sprite):
    def __init__(self, image, r0, **kwargs):
        '''
        Class for wrapping pyglet sprites so that we can work with arrays
        image: sprite appearance, png image,
        r0: initial position
        **kwargs: all other keyword arguments compatible with pyglet sprites,
        for example batch.
        '''
        super().__init__(image, r0[0], r0[1], **kwargs)

    def update(self, r, dtheta = 0):
        self.x = r[0] # update x
        self.y = r[1] # update y
        self.rotation += dtheta # optionally increment rotation

SYSTEM_SIZE = 30 # AU

width = 1920 #int(sys.argv[1]) # width
height = 1080# int(sys.argv[2]) # height
game_name = sys.argv[0].split('.')[0] # take game name from file name
window = pyglet.window.Window(width, height, caption = game_name)
#music = pyglet.resource.media('tocatta_and_fugue_in_D_minor.mp3')
#music.play()

controller = key.KeyStateHandler() # create a controller
window.push_handlers(controller) # connect controller to game window

all_bodies = pyglet.graphics.Batch() # draw everything at once in a Batch

n_planets = 7 # number of planets
n_bodies = 2 + n_planets # 1 sun, 1 player

to_screen = ScreenTransform(width, height, SYSTEM_SIZE, 1)
# create a solar system which does calculations
sol = SolarSystem(n_bodies, SYSTEM_SIZE)

# Load icons for solar system objects and player
background  = pyglet.image.load('./graphics/background.png')
player_icon = tools.load_sprite_image('./graphics/player.png')
star_icon = tools.load_sprite_image('./graphics/star.png')

bodies = [] # group all bodies in a list
# create player object
player = CelestialObject(player_icon, sol.r[0], batch = all_bodies)
star = CelestialObject(star_icon, sol.r[1], batch = all_bodies)
# add star first, then planets
bodies.append(player)
bodies.append(star)
for i in range(n_planets):
    planet_icon = tools.load_sprite_image(f'./graphics/p{i+1}.png')
    bodies.append(CelestialObject(planet_icon, sol.r[i+2], batch = all_bodies))

for i in range(n_bodies):
    bodies[i].scale *= 0.1

player.scale = 1

@window.event
def on_draw():
    # draw all objects in game window
    window.clear() # refresh
    background.blit(0,0) # blit happens
    all_bodies.draw()

dv = 5e-2 # boost level: to be replaced with momentum exchange
dtheta = 1 # gyroscopic rotation, in degrees
eating_distance = 1 # maximum distance at which planet is consumed

def update(dt):
    # this is where we update the window, and the game actually happens
    sol.update(dt) # update solar system motions
    # then shift from solar system coordinates to screen coordinates
    shifted = to_screen.transform(sol.r)
    # update the sprites (icons) accordingly
    for j, body in enumerate(bodies):
        body.update(shifted[j])

    # Check if any object is close enough to be converted to fuel
    dist_to_player = np.linalg.norm(sol.r[1:], axis = 1)
    close_enough = dist_to_player < eating_distance

    if np.any(close_enough):
        # if any object is close enough to player: convert it to fuel
        object_id = np.argmin(dist_to_player) + 1
        bodies[object_id].delete() # remove sprite
        del(bodies[object_id]) # and list entry
        sol.convert_to_fuel(object_id) # and remove object from calculations

    # Here comes the actual controls!
    if controller[key.W]:
        # perform boost in direction of spacecraft
        orientation = np.radians(player.rotation)
        boost = tools.unit_vector(orientation)*dv
        sol.v[0] = sol.v[0] + boost
    if controller[key.D]:
        # rotate clockwise
        player.rotation = tools.bound_angles(player.rotation + dtheta)
    if controller[key.A]:
        # rotate counterclockwise
        player.rotation = tools.bound_angles(player.rotation - dtheta)

    # zoom functionality
    if controller[key.O]:
        to_screen.zoom /= 1.1
        tools.scale_bodies(bodies, 0.9)
    if controller[key.P]:
        to_screen.zoom *= 1.1
        tools.scale_bodies(bodies, 1.1)

pyglet.clock.schedule_interval(update, 1/60.0) # update game every 1/60 seconds

if __name__ == '__main__':
    pyglet.app.run()
