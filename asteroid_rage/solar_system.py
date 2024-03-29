import numpy as np
import utils
# Init constants
G = 39.478 # AU^3/yr^-2 M_o^-1

class SolarSystem:
    def __init__(self, n_bodies, scale):
        # Solar system with n_bodies in it
        self.n_bodies = n_bodies
        self.scale = scale # bounds of solar system, [AU]
        self.rf = 0 # select reference frame to be object 0, i.e. player
        r, v, m, rho = self.initialize_system()
        self.r = r # positions
        self.v = v # velocities
        self.m = m # masses
        self.rho = rho # densities
        self.radius = (self.m/(self.rho*4/3*np.pi))**(1/3)*500 # radii

    def update(self, dt):
        # Euler-Chromer for starters
        acc = gravity_acc(self.r, self.m)
        self.v = self.v + dt*acc
        self.v = self.v - self.v[self.rf] # shift reference frame
        self.r = self.r + self.v*dt - self.r[self.rf]

    def initialize_system(self):
        # Generate initial positions r0, velocities v0, and masses m0
        r0 = np.random.uniform((-self.scale, -self.scale),\
                               (self.scale, self.scale), (self.n_bodies, 2))
        m0 = np.random.uniform(1e-6, 1e-2, self.n_bodies)   # solar masses
        rho = np.random.uniform(1e6, 1e7, self.n_bodies) # solar masses/au^3
        rho[1] = 2.3e6  # mean solar density, solar masses/au^3

        # Assign player to index 0, sun to index 1, and other bodies after
        r0[0] = np.array([self.scale, 0])
        m0[1] = 1 # mass in solar masses
        m0[0] = 1e-4
        v0 = vis_viva(r0) # elliptical orbits, semimajor axis given by r0
        r0[1] = 0 # initialize sun at centre
        v0[1] = 0 # sun at rest in centre of system
        return r0, v0, m0, rho

def vis_viva(r0):
    # find (initial) velocity of elliptical orbit using vis viva equation
    a = np.linalg.norm(r0, axis = -1, keepdims = True) # semimajor  axis
    rad_vec = r0/a
    tan_vec = utils.tangent_vector(rad_vec)
    return np.sqrt(G*1/a)*tan_vec

def gravity_acc(r, m):
    # calculate n body problem in inefficient manner :(
    d = r - r[:, np.newaxis] # find all distances
    f = np.zeros((len(r), len(r)-1, 2)) # forces
    indices = np.arange(len(r))
    for i in range(len(r)):
        mask = indices != i # do not include the body itself
        f[i] = G*m[mask, None]/np.linalg.norm(d[i, mask], axis = -1, keepdims = True)**3*d[i,mask]
    return np.sum(f, axis = 1)
