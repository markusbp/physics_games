import numpy as np

import tools
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
        self.rho = rho

    def update(self, dt):
        # Euler-Chromer for starters
        acc = gravity_acc(self.r, self.m)
        self.v = self.v + dt*acc
        self.v = self.v - self.v[self.rf] # shift reference frame
        self.r = self.r + self.v*dt - self.r[self.rf]

    def convert_to_fuel(self, id):
        # removes body no. id from arrays r,v and m, and adds its mass to player
        gained_mass = self.m[id]
        self.m[0] = self.m[0] + gained_mass
        self.r = np.delete(self.r, id, axis = 0)
        self.v = np.delete(self.v, id, axis = 0)
        self.m = np.delete(self.m, id, axis = 0)
        return gained_mass

    def initialize_system(self):
        # Generate initial positions r0, velocities v0, and masses m0
        r0 = np.random.uniform((-self.scale, -self.scale),\
                               (self.scale, self.scale), (self.n_bodies, 2))
        m0 = np.random.uniform(1e-6, 1e-2, self.n_bodies)   # solar masses
        rho = np.random.uniform(1e6, 1e7, self.n_bodies) # solar masses/au^3
        rho[1] = 1e6
        # Assign player to index 0, sun to index 1, and other bodies after
        # Shift system so that star is at center of screen
        r0[1] = 0 # initialize sun at centre
        m0[1] = 1 # mass in solar masses
        v0 = vis_viva(r0) # elliptical orbits, semimajor axis given by r0
        v0[1] = 0 # sun at rest in centre of system
        return r0, v0, m0, rho

def vis_viva(r0):
    # find (initial) velocity of elliptical orbit using vis viva equation
    a = np.linalg.norm(r0, axis = -1, keepdims = True)
    rad_vec = r0/a
    tan_vec = tools.tangent_vector(rad_vec)
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
