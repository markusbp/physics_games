# https://github.com/Harrelix/Asteroids/blob/master/Asteroids/Asteroids.py

import pygame
import numpy as np

import utils
import game_tools as gt
from screen_transform import ScreenTransform

SYSTEM_SIZE = 30 # AU

width = 1000 #int(sys.argv[1]) # width
height = 800 # height

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Asteroid Rage')

clock = pygame.time.Clock()

n_planets = 7 # number of planets
n_bodies = 2 + n_planets # 1 sun, 1 player

# transform object to convert from solar system to screen coordinates
transform = ScreenTransform(width, height, SYSTEM_SIZE, 1)
# create a solar system which does calculations
sol = gt.StudentSolarSystem(n_bodies, SYSTEM_SIZE)

# Load icons for solar system objects and player
background  = pygame.image.load('./graphics/background.png').convert()
player_icon = pygame.image.load('./graphics/player.png').convert()
star_icon = pygame.image.load('./graphics/star.png').convert()

print(sol.radius)
sizes = transform.size_transform(sol.radius[:, None])*5
print(sizes[0])

background_surface = pygame.Surface(background.get_size(), pygame.SRCALPHA)
background_surface.blit(background, background.get_rect())
# create player object
player = gt.CelestialObject(player_icon, sol.r[0], sizes[0])
star = gt.CelestialObject(star_icon, sol.r[1], sizes[1])
# add star first, then planets

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(star)

for i in range(n_planets):
    planet_icon = pygame.image.load(f'./graphics/p{i+1}.png')
    planet = gt.CelestialObject(planet_icon, sol.r[i+2], sizes[i+2])
    all_sprites.add(planet)


def play():
    thrust = -1e-5 # units?!
    flow_rate = 1e-7 # units!
    dtheta = 5 # gyroscopic rotation, in degrees
    eating_distance = 10 # maximum distance at which planet is consumed
    dry_mass = 1e-4
    dm = 1e-8
    dt = 0.01

    running = True
    while running:
        # this is where we update the window, and the game actually happens
        sol.update(dt) # update solar system motions with time step dt
        # then shift from solar system coordinates to screen coordinates
        screen_coordinates = transform(sol.r)
        # update the sprites (icons) accordingly
        for i, sprite in enumerate(all_sprites):
            sprite.update(screen_coordinates[i])

        screen.fill([0,0,0])
        background_rect = background_surface.get_rect()
        background_rect.center = screen_coordinates[1]
        screen.blit(background_surface, background_rect)
        all_sprites.draw(screen)
        # Collision detection + fuel conversion
        # Check if any object is close enough to be converted to fuel
        dist_to_player = np.linalg.norm(sol.r[1:], axis = 1) - sol.radius[1:]  # distance to surface
        ################################# Add sol.r[0] - ... for different reference frames!
        close_enough = dist_to_player < eating_distance
        too_close = dist_to_player < 0 # inside surface --> collision

        pygame.event.pump() # process event queue
        keys = pygame.key.get_pressed()

        if np.any(close_enough):
            # if any object is close enough to player: convert it to fuel
            if np.any(too_close):
                sys.exit() # if too close, game over

            if keys[pygame.K_SPACE]:
                object_id = np.argmin(dist_to_player) + 1 # closest object to player
                consumed = sol.convert_to_fuel(object_id, dm) # and remove object from calculations
                if consumed:
                    all_sprites[object_id].kill() # remove sprite

        # Here comes the actual controls!
        # Boosting
        if keys[pygame.K_w]:# and sol.m[0] > dry_mass:
            # perform boost in direction of spacecraft
            orientation = np.radians(player.rotation)
            boost = utils.unit_vector(orientation)*thrust/sol.m[0] # acceleration
            sol.v[0] = sol.v[0] + boost*dt
            sol.m[0] = sol.m[0] - flow_rate*dt
        #elif sol.m[0] < dry_mass:
        #    pass

        # Ship rotation
        if keys[pygame.K_d]:
            # rotate clockwise
            player.rotate(-dtheta)
        if keys[pygame.K_a]:
            # rotate counterclockwise
            player.rotate(dtheta)

        # zoom functionality
        if keys[pygame.K_DOWN]:
            transform.zoom *= 0.975
            new_size = (int(width*0.975), int(height*0.975))
            pygame.transform.scale(screen, new_size)
        if keys[pygame.K_UP]:
            transform.zoom *= 1.025
            new_size = (int(width*1.025), int(height*1.025))
            pygame.transform.scale(screen, new_size)
        # Change simulation speed
        if keys[pygame.K_COMMA]:
            dt *= 0.99
        if keys[pygame.K_PERIOD]:
            dt *= 1.01

        pygame.display.update()
        clock.tick(60) # run at 60 FPS (hopefully)

if __name__ == '__main__':
    play()
