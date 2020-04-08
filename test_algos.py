import numpy as np
import pytest

import tools

def test_n_body():
    n = 10

def test_integrator():
    pass

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
    r0 = np.array([-30, 0])
    height = 1080
    result = [0, int(height/2)]
    shifted = tools.transform(r0)
    print('Result', result, 'Shifted', shifted)
    assert result == pytest.approx(shifted)
