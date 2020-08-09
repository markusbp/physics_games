import numpy as np

# module for creating some simple tools for use in main project

def bound_angles(theta):
    # make sure player rotation is in [0, 360] degrees
    return theta % 360

def unit_vector(angle):
    # return a unit vector with oriented along angle
    return np.array([np.sin(angle), np.cos(angle)])

def tangent_vector(r):
    # return vector perpendicular to r (counterclockwise) --> [x, y] -> [-y, x]
    return np.flip(r, axis = -1)*np.array([-1, 1])

def transform(coord, scale, center):
    # shift coord from [-system size, system size] to [height, width]*zoom
    return coord*np.amin(center)/(scale) + center
