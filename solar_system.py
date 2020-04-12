import numpy as np

# Init constants
G = 39.478 # AU^3/yr^-2 M_o^-1

class SolarSystem:
    def __init__(self, n_bodies, ref_frame, scale):
        self.n_bodies = n_bodies
        self.rf = ref_frame # select reference frame to be object 1, i.e. sun!
        self.scale = scale
        r, v, m = self.initialize_system()
        self.r = r # positions
        self.v = v # velocities
        self.m = m # masses

    def update(self, dt):
        # Euler-Chromer for starters
        acc = gravity_acc(self.r, self.m)
        self.v = self.v + dt*acc
        self.v = self.v - self.v[self.rf] # shift reference frame
        self.r = self.r + self.v*dt

    def convert_to_fuel(self, id):
        # removes body no. id from arrays r,v and m, and adds its mass to player
        gained_mass = self.m[id]
        self.m[0] = self.m[0] + gained_mass
        self.r = np.delete(self.r, id, axis = 0)
        self.v = np.delete(self.v, id, axis = 0)
        self.m = np.delete(self.m, id, axis = 0)
        if id == self.rf:
            self.rf = 0
        return gained_mass

    def initialize_system(self):
        # Generate initial positions r0, velocities v0, and masses m0
        r0 = np.random.uniform((-self.scale, -self.scale),\
                               (self.scale, self.scale), (self.n_bodies, 2))
        v0 = np.random.uniform((-0.1, -0.1), (1.1, 1.1), (self.n_bodies, 2))
        m0 = np.random.uniform(1e-6, 1e-2, self.n_bodies)   # solar masses
        # Assign player to index 0, sun to index 1, and other bodies after
        # Shift system so that star is at center of screen
        r0[1] = 0
        v0[1] = 0 # heliocentricity, sun at rest
        m0[1] = 1 # solar masses
        return r0, v0, m0

def gravity_acc(r, m):
    d = r - r[:, np.newaxis] # find all distances
    f = np.zeros((len(r), len(r)-1, 2))
    indices = np.arange(len(r))
    # calculate n body problem in inefficient manner :(
    for i in range(len(r)):
        mask = indices != i # do not include the body itself
        f[i] = G*m[mask, None]/np.linalg.norm(d[i, mask], axis = -1, keepdims = True)**3*d[i,mask]
    return np.sum(f, axis = 1)
