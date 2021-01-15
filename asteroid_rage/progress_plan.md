# Progress Plan

1. Create a simple background, a starry sky - OK
2. Create a pyglet game window, learn some of the API, set background - OK
3. Create a solar system  - OK, but needs more work
   - Should this be object oriented --> Inherit from pyglet sprites - sort of
   - Create Solar System as a collection of objects - Yup!
   - Each celestial body should have mass, radius, position, and initial velocity - Radius could be added
   - To compute things more efficiently, store all positions/velocities together? - Yup
4. Create a spacecraft/player - OK
   - Object oriented? Should inherit from pyglet sprites
   - Should have mass, size (?), velocity and orientation/rotation
5. Create an integrator - OK
   - Leapfrog integration to simulate motion of all objects? Or Euler-Chromer - EC to start
6. Create test algorithms. Test integrator, use pytest
7. Add propulsion to rocket. Rocket equation, or just Newton's third law? - OK
8. Add tractor beam to rocket - for consuming planets?
9. Add controls to spacecraft - OK
   - Rotation and thrust - OK
   - Optional thrust level?
11. Add impact: Ship "explodes" if too close to other objects? - only exits
12. Add goal: To either eat, or reach the star at the center - eat all bodies
13. Add timer to see how fast players are - OK
14. Play!
