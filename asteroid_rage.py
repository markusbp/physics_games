import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt
from pyglet.window import key # controller

import tools
from solar_system import SolarSystem
from screen_transform import ScreenTransform

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
music = pyglet.resource.media('tocatta_and_fugue_in_D_minor.mp3')
music.play()

controller = key.KeyStateHandler() # create a controller
window.push_handlers(controller) # connect controller to game window

main_batch = pyglet.graphics.Batch() # draw everything at once in a Batch

n_planets = 7 # number of planets
n_bodies = 2 + n_planets # 1 sun, 1 player

# transform object to convert from solar system to screen coordinates
transform = ScreenTransform(width, height, SYSTEM_SIZE, 1)
# create a solar system which does calculations
sol = SolarSystem(n_bodies, SYSTEM_SIZE)

# Load icons for solar system objects and player
background  = pyglet.image.load('./graphics/background.png')
player_icon = tools.load_sprite_image('./graphics/player.png')
star_icon = tools.load_sprite_image('./graphics/star.png')

bodies = [] # group all bodies in a list
# create player object
player = CelestialObject(player_icon, sol.r[0], batch = main_batch)
star = CelestialObject(star_icon, sol.r[1], batch = main_batch)
# add star first, then planets
bodies.append(player)
bodies.append(star)
for i in range(n_planets):
    planet_icon = tools.load_sprite_image(f'./graphics/p{i+1}.png')
    bodies.append(CelestialObject(planet_icon, sol.r[i+2], batch = main_batch))

for i in range(n_bodies):
    bodies[i].scale = sol.radius[i]*2*transform.scale
player.scale = 0.1

time_label = pyglet.text.Label('Time: 0', x = width*0.9, y = height*0.95, batch=main_batch)
fuel_label = pyglet.text.Label('Fuel: %.3E' %(sol.m[0]), x = width*0.904, y = height*0.93, batch=main_batch)


dv = 5e-2 # boost level: to be replaced with momentum exchange
dtheta = 2 # gyroscopic rotation, in degrees
eating_distance = 0.1 # maximum distance at which planet is consumed

time = [0]

@window.event
def on_draw():
    # draw all objects in game window
    window.clear() # refresh
    background.blit(0,0) # blit happens
    main_batch.draw()


def update(dt):
    time[0] += dt
    time_label.text = 'Time: ' + str(time)[1:8]
    # this is where we update the window, and the game actually happens
    sol.update(dt) # update solar system motions
    # then shift from solar system coordinates to screen coordinates
    shifted = transform(sol.r)
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
        fuel_label.text = 'Fuel: %.3E' %(sol.m[0])
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
    if controller[key.DOWN]:
        transform.zoom /= 1.05
        tools.scale_bodies(bodies, 0.95)
    if controller[key.UP]:
        transform.zoom *= 1.05
        tools.scale_bodies(bodies, 1.05)

pyglet.clock.schedule_interval(update, 1/120.0) # update game every 1/60 seconds

if __name__ == '__main__':
    pyglet.app.run()
