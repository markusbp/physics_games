import pyglet
import numpy as np

from solar_system import SolarSystem
# module for game-related tools

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

    def zoom(self, zoom_factor):
        self.scale *= zoom_factor

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

def load_sprite_image(filename):
    # load sprite image, and anchor to its center!
    img = pyglet.image.load(filename)
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img
