import numpy as np

class ScreenTransform:
    def __init__(self, width, height, system_size, zoom = 1):
        '''
        Handles transform from physical coordinates to screen coordinates
        width: screen width
        height: screen height
        system_size: scale of solar system in AU
        zoom: zoom factor; allows us to change scale
        '''
        self.width = width
        self.height = height
        self.system_size = system_size # solar system scale
        self._zoom = zoom # optional zoom level
        # center of screen
        self.center = np.array([int(width/2), int(height/2)])
        self.scale = np.amin(self.center)/(self.system_size)*self._zoom

    def __call__(self, coord):
        # shift coord from [-system size, system size] to [height, width]*zoom
        return coord*self.scale + self.center

    @property
    def zoom(self):
        # set zoom: @property allows us to use a setter
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        # setter allows us to change scale factor correctly when zoom changes
        self._zoom = zoom
        self.scale = np.amin(self.center)/(self.system_size)*self._zoom
