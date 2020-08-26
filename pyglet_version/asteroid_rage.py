import sys
import time
import pyglet
import numpy as np

from pyglet.window import key # controller

import utils
import game_tools as gt
from screen_transform import ScreenTransform

SYSTEM_SIZE = 30 # AU

WIDTH = 1920 # width
HEIGHT = 1080 # height
game_name = 'Asteroid Rage' # take game name from file name
window = pyglet.window.Window(WIDTH, HEIGHT, caption = game_name)

controller = key.KeyStateHandler() # create a controller
window.push_handlers(controller) # connect controller to game window

n_planets = 7 # number of planets
n_bodies = 2 + n_planets # 1 sun, 1 player

# transform object to convert from solar system to screen coordinates
transform = ScreenTransform(WIDTH, HEIGHT, SYSTEM_SIZE, 1)
# create a solar system which does calculations
sol = gt.StudentSolarSystem(n_bodies, SYSTEM_SIZE)

# Load icons for solar system objects and player
background_img  = gt.load_sprite_image('./graphics/background.png')
player_icon = gt.load_sprite_image('./graphics/player.png')
player_eat_icon = gt.load_sprite_image('./graphics/player_consume.png')
star_icon = gt.load_sprite_image('./graphics/star.png')

main_batch = pyglet.graphics.Batch() # draw everything at once in a Batch
background = pyglet.graphics.OrderedGroup(0) # background first
foreground = pyglet.graphics.OrderedGroup(1) # then foreground
background_sprite = gt.BackgroundSprite(background_img, sol.r[1],\
                                       batch = main_batch, group = background)

bodies = [] # group all bodies in a list
# create player object
player = gt.CelestialObject(player_icon, sol.r[0], batch = main_batch, group = foreground)
star = gt.CelestialObject(star_icon, sol.r[1], batch = main_batch, group = foreground)
# add star first, then planets
bodies.append(player)
bodies.append(star)
for i in range(n_planets):
    planet_icon = gt.load_sprite_image(f'./graphics/p{i+1}.png')
    bodies.append(gt.CelestialObject(planet_icon, sol.r[i+2], batch = main_batch, group = foreground))

for i in range(n_bodies):
    bodies[i].scale = sol.radius[i]*2*transform.scale/bodies[i].width

player.scale *= 2

t_zero = time.time()

THRUST = 1e-4 # units?!
FLOW_RATE = 1e-5 # units!
DTHETA = 2 # gyroscopic rotation, in degrees
EAT_DISTANCE = 1 # AU, maximum distance at which planet is consumed
DRY_MASS = 1e-5 # mass of space ship without fuel (solar masses)
DM = 1e-4 # rate at which objects are consumed
VARS = {'time': t_zero, 'dt' : 1/100, 'was_close' : False}

time_label = pyglet.text.Label('Time: 0', x = WIDTH*0.89, y = HEIGHT*0.95,
                                batch = main_batch, group = foreground)
sim_label = pyglet.text.Label('Sim. Speed: %.3f' %(0), batch = main_batch, group = foreground,
                                x = WIDTH*0.89, y = HEIGHT*0.93)
progress_label = pyglet.text.Label(f'Objects Consumed: {0}/{n_bodies - 1} ',
                                   batch = main_batch, group = foreground,
                                   x = WIDTH*0.89, y = HEIGHT*0.91)
mass_label = pyglet.text.Label(f'Fuel: %.3E' %(sol.m[0] - DRY_MASS), batch = main_batch, group = foreground,
                                x = WIDTH*0.89, y = HEIGHT*0.89)

@window.event
def on_draw():
    # draw all objects in game window
    window.clear() # refresh
    main_batch.draw()

def update(refresh_rate):
    # Controls first, see if anything has happened

    # zoom functionality
    if controller[key.DOWN]:

        transform.zoom *= 0.975
        for body in bodies:
            body.zoom(0.975)

    if controller[key.UP]:
        transform.zoom *= 1.025
        for body in bodies:
            body.zoom(1.025)

    # Boosting
    if controller[key.W] and sol.m[0] > DRY_MASS:
        # perform boost in direction of spacecraft
        orientation = np.radians(player.rotation)
        boost = utils.unit_vector(orientation)*THRUST/sol.m[0] # acceleration
        sol.v[0] = sol.v[0] + boost*VARS['dt']
        sol.m[0] = sol.m[0] - FLOW_RATE*VARS['dt']
        mass_label.text = f'Fuel: %.3E' %(sol.m[0] - DRY_MASS)
    elif sol.m[0] < DRY_MASS:
        mass_label.text = f'Fuel: Empty'
    # Ship rotation
    if controller[key.D]:
        # rotate clockwise
        player.rotation = utils.bound_angles(player.rotation + DTHETA)
    if controller[key.A]:
        # rotate counterclockwise
        player.rotation = utils.bound_angles(player.rotation - DTHETA)

    # Change simulation speed
    if controller[key.COMMA]:
        VARS['dt'] *= 0.98
        sim_label.text = 'Sim. Speed: %.3f' %(VARS['dt'])
    if controller[key.PERIOD]:
        VARS['dt'] *= 1.02
        sim_label.text = 'Sim. Speed: %.3f' %(VARS['dt'])

    VARS['time'] = time.time() - t_zero #VARS['dt'] # update time
    time_label.text = 'Time: %.2f' %(VARS['time'])
    # this is where we update the window, and the game actually happens
    sol.update(VARS['dt']) # update solar system motions with time step dt
    # then shift from solar system coordinates to screen coordinates
    screen_coordinates = transform(sol.r)
    # update the sprites (icons) accordingly
    background_sprite.update(sol.v[1]*VARS['dt']*transform.scale/transform.zoom) # update background to follow star
    for j, body in enumerate(bodies):
        body.update(screen_coordinates[j])

    # Collision detection + fuel conversion
    # Check if any object is close enough to be converted to fuel
    dist_to_player = np.linalg.norm(sol.r[1:], axis = 1) - sol.radius[1:]  # distance to surface
    ################################# Add sol.r[0] - ... for different reference frames!
    close_enough = np.any(dist_to_player < EAT_DISTANCE)

    # Change player sprite to indicate that planet is in range
    if VARS['was_close'] == True and close_enough == False:
        player.image = player_icon
        VARS['was_close'] = False
    elif close_enough and VARS['was_close'] == True:
        too_close = dist_to_player < 0 # inside surface --> collision
        if np.any(too_close):
            sys.exit() # if too close, game over

        if controller[key.SPACE]:
            object_id = np.argmin(dist_to_player) + 1
            consumed = sol.convert_to_fuel(object_id, DM) # and remove object from calculations
            mass_label.text = f'Fuel: %.3E' %(sol.m[0] - DRY_MASS)
            if consumed:
                bodies[object_id].delete() # remove sprite
                del(bodies[object_id]) # and list entry
                objects_consumed = n_bodies - len(bodies)
                progress_label.text = f'Objects Consumed: {objects_consumed}/{n_bodies - 1}'
                
    elif close_enough:
        VARS['was_close'] = True
        player.image = player_eat_icon


pyglet.clock.schedule_interval(update, 1/120.0) # update game every 1/120 seconds

if __name__ == '__main__':
    pyglet.app.run()
