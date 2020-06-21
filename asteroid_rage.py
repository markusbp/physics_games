import sys
import pyglet
import numpy as np
import matplotlib.pyplot as plt
from pyglet.window import key # controller

import utils
import game_tools as gt
from screen_transform import ScreenTransform

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
sol = gt.StudentSolarSystem(n_bodies, SYSTEM_SIZE)

# Load icons for solar system objects and player
background  = pyglet.image.load('./graphics/background.png')
player_icon = gt.load_sprite_image('./graphics/player.png')
star_icon = gt.load_sprite_image('./graphics/star.png')

bodies = [] # group all bodies in a list
# create player object
player = gt.CelestialObject(player_icon, sol.r[0], batch = main_batch)
star = gt.CelestialObject(star_icon, sol.r[1], batch = main_batch)
# add star first, then planets
bodies.append(player)
bodies.append(star)
for i in range(n_planets):
    planet_icon = gt.load_sprite_image(f'./graphics/p{i+1}.png')
    bodies.append(gt.CelestialObject(planet_icon, sol.r[i+2], batch = main_batch))

for i in range(n_bodies):
    bodies[i].scale = sol.radius[i]*2*transform.scale/bodies[i].width*1000
player.scale = 0.5

time_label = pyglet.text.Label('Time: 0', x = width*0.9, y = height*0.95, batch=main_batch)
fuel_label = pyglet.text.Label('Fuel: %.3E' %(sol.m[0]), x = width*0.904, y = height*0.93, batch=main_batch)

thrust = 1e-2 # units?!
flow_rate = 1e-3 # units!
dtheta = 2 # gyroscopic rotation, in degrees
eating_distance = 1 # maximum distance at which planet is consumed
dry_mass = 1e-4
dm = 1e-4
settings = {'time': 0, 'dt' : 1/120 }

@window.event
def on_draw():
    # draw all objects in game window
    window.clear() # refresh
    background.blit(0,0) # blit happens
    main_batch.draw()

def update(refresh_rate):
    settings['time'] += settings['dt'] # update time
    time_label.text = 'Time: %.2f' %(settings['time'])
    # this is where we update the window, and the game actually happens
    sol.update(settings['dt']) # update solar system motions with time step dt
    # then shift from solar system coordinates to screen coordinates
    screen_coordinates = transform(sol.r)
    # update the sprites (icons) accordingly
    for j, body in enumerate(bodies):
        body.update(screen_coordinates[j])

    # Collision detection + fuel conversion
    # Check if any object is close enough to be converted to fuel
    dist_to_player = np.linalg.norm(sol.r[1:], axis = 1) - sol.radius[1:]  # distance to surface
    ################################# Add sol.r[0] - ... for different reference frames!
    close_enough = dist_to_player < eating_distance
    too_close = dist_to_player < 0 # inside surface --> collision

    if np.any(close_enough):
        # if any object is close enough to player: convert it to fuel
        if np.any(too_close):
            sys.exit() # if too close, game over

        if controller[key.SPACE]:
            object_id = np.argmin(dist_to_player) + 1
            consumed = sol.convert_to_fuel(object_id, dm) # and remove object from calculations
            if consumed:
                bodies[object_id].delete() # remove sprite
                del(bodies[object_id]) # and list entry

            fuel_label.text = 'Fuel: %.3E' %(sol.m[0])

    # Here comes the actual controls!
    # Boosting
    if controller[key.W] and sol.m[0] > dry_mass:
        # perform boost in direction of spacecraft
        orientation = np.radians(player.rotation)
        boost = utils.unit_vector(orientation)*thrust/sol.m[0] # acceleration
        sol.v[0] = sol.v[0] + boost*settings['dt']
        sol.m[0] = sol.m[0] - flow_rate*settings['dt']
        fuel_label.text = 'Fuel: %.3E' %(sol.m[0])
    elif sol.m[0] < dry_mass:
        fuel_label.text = 'Fuel: Empty'

    # Ship rotation
    if controller[key.D]:
        # rotate clockwise
        player.rotation = utils.bound_angles(player.rotation + dtheta)
    if controller[key.A]:
        # rotate counterclockwise
        player.rotation = utils.bound_angles(player.rotation - dtheta)

    # zoom functionality
    if controller[key.DOWN]:
        transform.zoom *= 0.975
        gt.scale_bodies(bodies, 0.975)
    if controller[key.UP]:
        transform.zoom *= 1.025
        gt.scale_bodies(bodies, 1.025)

    # Change simulation speed
    if controller[key.COMMA]:
        settings['dt'] *= 0.99
    if controller[key.PERIOD]:
        settings['dt'] *= 1.01

pyglet.clock.schedule_interval(update, 1/120.0) # update game every 1/120 seconds

if __name__ == '__main__':
    pyglet.app.run()
