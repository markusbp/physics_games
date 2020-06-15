import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

def generate_sky(height, width):
    # generate a nice star-studded background for a solar system
    n_stars = 5000  # create 5000 "stars" to start with
    sky = np.zeros((height, width), dtype=np.uint8)  # empty sky, grayscale
    # Pick out random indices
    x = np.random.choice(height, n_stars)
    y = np.random.choice(width, n_stars)
    sky[x, y] = 255  # set these to "white"
    # smooth the image using gaussian filter, take median, then shift
    sky = ndimage.filters.gaussian_filter(sky, 1.2, mode='nearest')
    sky = ndimage.median_filter(sky, 9, mode='nearest')  # kernel window of 9
    sky = (sky - np.min(sky))/(np.max(sky)-np.min(sky))*255
    return sky

def generate_bg(height, width):
    # generate white background
    sky = np.ones((height, width), dtype = np.uint8)*255
    return sky

if __name__ == '__main__':
    w, h = int(sys.argv[1]), int(sys.argv[2])
    sky = generate_sky(h, w)
    # Save generated figure without axes
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(sky, aspect='auto', cmap = 'gray', vmin = 0, vmax = 255)
    fig.savefig('./graphics/background.png', dpi = 300)
