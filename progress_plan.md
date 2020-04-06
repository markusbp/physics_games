# Progress Plan

1. Create a simple background, a starry sky - OK
2. Create a pyglet game window, learn some of the API, set background
3. Create a solar system  
   - Should this be object oriented --> Inherit from pyglet sprites
   - Create Solar System as a collection of objects
   - Each celestial body should have mass, radius, position, and initial velocity
   - To compute things more efficiently, store all positions/velocities together?
4. Create a spacecraft/player
   - Object oriented? Should inherit from pyglet sprites
   - Should have mass, size (?), velocity and orientation/rotation
5. Create an integrator
   - Leapfrog integration to simulate motion of all objects? Or Euler-Chromer
6. Create test algorithms. Test integrator, use pytest
7. Add propulsion to rocket. Rocket equation, or just Newton's third law?
8. Add tractor beam to rocket - for consuming planets?
9. Add controls to spacecraft
   - Rotation and thrust
   - Optional thrust level?
11. Add impact: Ship "explodes" if too close to other objects?
12. Add goal: To either eat, or reach the star at the center
13. Add timer to see how fast players are
14. Play!
