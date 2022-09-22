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

    lat = float(lat)
    lon = float(lon)
    light = 0
    dust = 0
    fog = 0
    clouds = np.empty((2*rad+1, 2*rad+1), dtype="float")

    i = 0
    tmp = parameters['fog']['lastArray']
    while (not math.isclose(lat, tmp[0][i])) and (not math.isclose(lon, tmp[1][i])) and (i < len(tmp[0])):
        i += 1

    if i == len(tmp[0]):
        for i in range(len(clouds)):
            for j in range(len(clouds[i])):
                clouds[i][j] = 0
    else:
        light = parameters['night_overview']['lastArray'][2][i]
        dust = parameters['dust']['lastArray'][2][i]
        fog = parameters['fog']['lastArray'][2][i]

    return light, dust, fog, clouds
