import pyglet
import numpy as np

# module for creating some simple tools for use in main project
def load_sprite_image(filename):
    # load sprite image, and anchor to its center!
    img = pyglet.image.load(filename)
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img

def bound_angles(theta):
    # make sure player rotation is in [-360, 360] degrees
    if np.abs(theta) > 360:
        mod = theta%360
    else:
        mod = theta
    return mod

def unit_vector(angle):
    # return a unit vector with oriented along angle
    return np.array([np.sin(angle), np.cos(angle)])

def tangent_vector(r):
    return np.flip(r, axis = -1)*np.array([-1, 1])

def transform(coord, scale, center):
    # shift coord from [-system size, system size] to [height, width]*zoom
    return coord*np.amin(center)/(scale) + center

def scale_bodies(bodies, scale):
    for body in bodies:
        body.scale *= scale
