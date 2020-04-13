import numpy as np
import pytest

import tools

# Test module

def test_angle_bounds():
    angles = [360, 370, -500]
    bounded = [360, 10, 220]
    for theta, actual in zip(angles, bounded):
        theta = tools.bound_angles(theta)
        print('Theta', theta, 'Label', actual)
        assert theta == pytest.approx(actual)

def test_unit_vector():
    angles = [0, np.pi/2]
    expectors = [[0, 1], [1, 0]]
    for theta, vector in zip(angles, expectors):
        unit_vector = tools.unit_vector(theta)
        print('Calculated vector:', unit_vector, '\nActual vector:', vector)
        assert unit_vector == pytest.approx(vector)

def test_transform():
    # test that physical coordinates are transformed to screen coordinates correctly
    scale = 10
    r0 = np.array([0, -scale])
    width  = 1920
    height = 1080
    result = [int(width/2), 0]
    center = np.array([int(width/2), int(height/2)])
    shifted = tools.transform(r0, scale, center)
    print('Result', result, 'Shifted', shifted)
    assert result == pytest.approx(shifted)

# Next tests to be implemented: Test gravity_acc and n_body simulator. Must think about how
