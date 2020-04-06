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
    # smooth the image using gaussian filter, shift, then take median
    sky = ndimage.filters.gaussian_filter(sky, 1.2, mode='nearest')
    sky = (sky - np.min(sky))/(np.max(sky)-np.min(sky))*255
    sky = ndimage.median_filter(sky, 9, mode='nearest')  # kernel window of 9
    return sky


if __name__ == '__main__':
    sky = generate_sky(1080, 1920)
    plt.imshow(sky, cmap='gray')
    plt.show()
