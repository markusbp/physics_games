import pyglet

# module for game-related tools

class CelestialObject(pyglet.sprite.Sprite):
    def __init__(self, image, r0, **kwargs):
        '''
        Class for wrapping pyglet sprites so that we can work with arrays
        image: sprite appearance, png image,
        r0: initial position
        **kwargs: all other keyword arguments compatible with pyglet sprites,
        for example batch.
        '''
        super().__init__(image, r0[0], r0[1], **kwargs)

    def update(self, r, dtheta = 0):
        self.x = r[0] # update x
        self.y = r[1] # update y
        self.rotation += dtheta # optionally increment rotation

def scale_bodies(bodies, scale):
    for body in bodies:
        body.scale *= scale

def load_sprite_image(filename):
    # load sprite image, and anchor to its center!
    img = pyglet.image.load(filename)
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img
