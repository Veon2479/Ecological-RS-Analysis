import math

import numpy as np
from numpy import array
from pyresample.geometry import AreaDefinition
import cv2
from . import lightAnal as anal
# import lightAnal as anal
import os

area = AreaDefinition(
    area_id='Belarus',
    description='The region of Belarus (WGS 84 / UTM zone 35N Projection)',
    projection='EPSG:32635',
    proj_id='EPSG:32635',
    width=2800,
    height=2400,
    area_extent=(
        200000,
        5650000,
        900000,
        6250000,
    ))

SRC_PATH = os.path.dirname(os.path.realpath(__file__))
REL_PATH = '\\..\\meteo_data\\'
FULL_PATH = (SRC_PATH + REL_PATH).replace('\\', '/')
EXT = '.tif'

ZT = 5  # zero threshold - this amount is held on image to zero it

parameters = dict(
    night_overview=dict(name='night_overview', lower=np.array([0, 75 - ZT, 75 - ZT]),
                        upper=np.array([255, 255, 255]), threshold=75/255., value_func=anal.value_fun_light,
                        lastArray=[]),
    fog=dict(name='night_fog', lower=np.array([0, 10 - ZT, 0]),
             upper=np.array([255, 255, 255]), threshold=10/255., value_func=anal.value_fun_fog,
             lastArray=[]),
    dust=dict(name='dust', lower=np.array([140 - ZT, 0, 180 - ZT]),
              upper=np.array([255, 140 + ZT, 255]), threshold=0.0, value_func=anal.value_fun_dust,
              lastArray=[]),
    cloudtop=dict(name='cloudtop', lower=np.array([0, 114 - ZT, 114 - ZT]),
                  upper=np.array([255, 255, 255]), threshold=0.0, value_func=anal.value_fun_cloudtop,
                  lastArray=[])

    # dust=dict(name='dust', lower=np.array([199, 20, 133]),
    #               upper=np.array([255, 192, 203]), threshold=50)
)


def get_all_data(lat, lon, rad):
    data = dict.fromkeys(['night_overview', 'fog', 'dust', 'cloudtop'])
    # finding size of parameter "matrix"
    kx = 1
    ky = 1
    i = 0
    if math.isclose(parameters['fog']['lastArray'][0][0], parameters['fog']['lastArray'][0][1]): # pre-last 0 means lat
        while not math.isclose(parameters['fog']['lastArray'][0][0], parameters['fog']['lastArray'][0][i]):
            i += 1
        ky = i + 1
    else:
        while not math.isclose(parameters['fog']['lastArray'][1][0], parameters['fog']['lastArray'][1][i]):
            i += 1
        kx = i + 1
    # [i*kx + j*ky] = [i, j]
    i = 0
    j = 0
    # finding central element of result matrix
    while not math.isclose(parameters['fog']['lastArray'][0][i], lat):
        i += kx
    while not math.isclose(parameters['fog']['lastArray'][1][i], lon):
        j += ky

    # filling result matrix
    i -= kx * rad
    j -= ky * rad

    for itI in range(2 * rad):
        for itJ in range(2 * rad):
            num = i * kx + j * ky
            tmp = array(0, 0, 0, 0)
            if (num >= 0) and (num < len(parameters['fog']['lastArray'][0])):
                tmp = {parameters['night_overview']['lastArray'][2][num],
                       parameters['fog']['lastArray'][2][num],
                       parameters['dust']['lastArray'][2][num],
                       parameters['cloudtop']['lastArray'][2][num]}
            data['night_overview'][itI][itJ] = tmp[0]
            data['fog'][itI][itJ] = tmp[1]
            data['dust'][itI][itJ] = tmp[2]
            data['cloudtop'][itI][itJ] = tmp[3]
            j += ky
        i += kx

    return data
