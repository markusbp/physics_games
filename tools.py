import pyglet
import numpy as np

def load_sprite_image(filename):
    # load sprite image, and anchor to its center!
    img = pyglet.image.load(filename)
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img

def bound_angles(theta):
    if np.abs(theta) > 360:
        mod = theta%360
    else:
        mod = theta
    return mod

def unit_vector(angle):
    return np.array([np.sin(angle), np.cos(angle)])
