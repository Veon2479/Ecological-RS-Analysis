import numpy as np
from pyresample.geometry import AreaDefinition
import cv2
from . import lightAnal as anal
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

parameters = dict(
    night_overview=dict(name='night_overview', lower=np.array([0, 75, 75]),
                        upper=np.array([255, 255, 255]), threshold=1E-12, value_func=anal.value_fun_light,
                        lastArray = []),
    fog=dict(name='night_fog', lower=np.array([0, 10, 0]),
             upper=np.array([255, 255, 255]), threshold=1E-12, value_func=anal.value_fun_fog,
             lastArray = []),
    dust=dict(name='dust', lower=np.array([140, 0, 180]),
              upper=np.array([255, 140, 255]), threshold=1E-12, value_func=anal.value_fun_dust,
              lastArray = []),
    cloudtop=dict(name='cloudtop', lower=np.array([0, 114, 114]),
                  upper=np.array([255, 255, 255]), threshold=1E-12, value_func=anal.value_fun_cloudtop,
                  lastArray = [])

    # dust=dict(name='dust', lower=np.array([199, 20, 133]),
    #               upper=np.array([255, 192, 203]), threshold=50)
)
