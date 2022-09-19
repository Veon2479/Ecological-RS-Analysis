import numpy as np


def value_fun_dust(color_array):
    r = color_array[2]
    r = (r - 180) / (255 - 180.)
    g = color_array[1]
    g = (255 - g) / (255 - 140.)

    return r * g


def value_fun_fog(color_array):
    return color_array[1] / 255.  # max(color_array[1] - 160, 160) / float(255 - 160)


def value_fun_light(color_array):
    return color_array[1] / 255.


def fft_filter(channel, mask):
    f = np.fft.fft2(channel)
    fshift = np.fft.fftshift(f)

    # In the lines following, we'll make a copy of the original spectrum and
    ifshift = np.multiply(fshift, mask)

    ishift = np.fft.ifftshift(ifshift)
    iimg = np.fft.ifft2(ishift)
    iimg = np.abs(iimg)
    imax = iimg.max() / 255.
    iimg = iimg / imax
    return iimg.astype(np.uint8)
