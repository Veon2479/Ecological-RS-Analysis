import math
from typing import List, Set, Any

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
                        upper=np.array([255, 255, 255]), threshold=75 / 255., value_func=anal.value_fun_light,
                        lastArray=[]),
    fog=dict(name='night_fog', lower=np.array([0, 10 - ZT, 0]),
             upper=np.array([255, 255, 255]), threshold=10 / 255., value_func=anal.value_fun_fog,
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
    dust = 0
    fog = 0
    light = np.empty((2 * rad + 1, 2 * rad + 1), dtype="float")
    clouds = np.empty((2 * rad + 1, 2 * rad + 1), dtype="float")

    i = 0
    tmp = parameters['fog']['lastArray']
    while (i < len(tmp[0]) and (not math.isclose(lat, float(tmp[0][i]), rel_tol=1e-3))) and \
            (not math.isclose(lon, float(tmp[1][i]), rel_tol=1e-3)):
        i += 1
    print(i)
    k = 0
    j = 0
    if i == len(tmp[0]):
        for k in range(0, len(clouds)):
            for j in range(0, len(clouds[k])):
                clouds[k][j] = 0
                light[k][j] = 0
        print("nope")
    else:
        dust = parameters['dust']['lastArray'][2][i]
        fog = parameters['fog']['lastArray'][2][i]

        cloud_data = parameters['cloudtop']['lastArray']
        light_data = parameters['night_overview']['lastArray']

        latlist = list()
        for j in range(0, len(cloud_data[0])):
            if math.isclose(lat, cloud_data[0][j], rel_tol=1e-3):
                latlist.append({float(cloud_data[0][j]), float(cloud_data[1][j]),
                                float(cloud_data[2][j]), float(light_data[2][j])})

        latlist.sort(key=lambda t: t[0])

        j = 0
        while (j < len(latlist)) and (not math.isclose(lon, float(latlist[j][1]), rel_tol=1e-3)):
            j += 1

        for k in range(0, 2 * rad + 1):
            if 0 <= (j - rad + k) < len(latlist):
                clouds[k][rad + 1] = latlist[j - rad + k][2]
                clouds[k][rad + 1] = latlist[j - rad + k][3]

        for k in range(0, 2 * rad + 1):
            if k != rad + 1:
                lonlist = list()

                for q in range(0, len(cloud_data[1])):
                    if 0 <= j - rad + q < len(latlist):
                        if math.isclose(float(latlist[j - rad + q][1]), cloud_data[1][q], rel_tol=1e-3):
                            lonlist.append({float(cloud_data[0][q]), float(cloud_data[1][q]),
                                            float(cloud_data[2][q]), float(light_data[2][q])})
                lonlist.sort(key=lambda row: row[0])

                z = 0
                if 0 <= j - rad + k < len(latlist):
                    while (z < len(lonlist)) and \
                            (not math.isclose(float(latlist[j - rad + k][0]), float(lonlist[z][0]), rel_tol=1e-3)):
                        z += 1

                for q in range(0, 2 * rad + 1):
                    if q != rad + 1 and 0 <= z - rad + q < len(lonlist):
                        clouds[k][q] = lonlist[z - rad + q][2]
                        light[k][q] = lonlist[z - rad + q][3]

    print("dust is ", dust)
    print("fog is ", fog)
    print("clouds are ", clouds[rad + 1][rad + 1])
    print("light are ", light[rad + 1][rad + 1])

    return light, dust, fog, clouds
