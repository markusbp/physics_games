import pygame
import numpy as np

from solar_system import SolarSystem
import utils
# module for game-related tools

class CelestialObject(pygame.sprite.Sprite):
    def __init__(self, image, r0, scale, **kwargs):
        '''
        Class for wrapping pygame sprites so that we can work with arrays
        image: sprite appearance, png image,
        r0: initial position
        **kwargs: all other keyword arguments compatible with pygame sprites,
        for example batch.
        '''
        size = image.get_size()*scale
        self.icon = pygame.transform.scale(image, size.astype('int')) # sprite image
        self.image = self.icon.copy() # make copy of image to display
        self.rect = self.image.get_rect()
        self.rect.center = r0
        self.rotation = 0 # sprite rotation
        super().__init__(**kwargs)

    def update(self, r):
        self.rect.center = r # update x

    def rotate(self, dtheta):
        # Rotate sprite image an angle dtheta
        center = self.rect.center # get previous position
        self.rotation += dtheta
        self.rotation = utils.bound_angles(self.rotation) # ensure angle is in [0, 360]
        display_image = self.icon.copy() # make new copy of original image
        self.image = pygame.transform.rotate(display_image, self.rotation)
        self.rect = self.image.get_rect(center = center)

    def zoom(self, zoom):
        center = self.rect.center # get previous position
        display_image = self.icon.copy() # make new copy of original image
        new_size = self.image.get_size()*np.array([zoom])
        self.image = pygame.transform.scale(display_image, new_size.astype('int'))
        self.rect = self.image.get_rect(center = center)

class StudentSolarSystem(SolarSystem):
    def convert_to_fuel(self, id, dm):
        # removes body no. id from arrays r,v and m, and adds its mass to player
        after_mass = self.m[id] - dm
        if after_mass < 0:
            self.m[0] = self.m[0] + self.m[id]
            self.r = np.delete(self.r, id, axis = 0)
            self.v = np.delete(self.v, id, axis = 0)
            self.m = np.delete(self.m, id, axis = 0)
            self.radius = np.delete(self.radius, id, axis = 0)
            self.rho = np.delete(self.rho, id, axis = 0)
            consumed = True
        else:
            self.m[0] = self.m[0] + dm
            self.m[id] = self.m[id] - dm
            consumed = False
        return consumed
