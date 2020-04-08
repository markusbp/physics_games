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
