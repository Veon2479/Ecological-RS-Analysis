# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import json
# import matplotlib.pyplot as plt
# import pandas as pd

# Feature Scaling
# from sklearn.preprocessing import MinMaxScaler

# neural network
# f rom tensorflow import keras
# from keras.optimizers import RMSprop
# from keras.callbacks import Callback
# from keras.models import Sequential
# from keras.layers import LSTM, Dense, Dropout, Bidirectional, SimpleRNN

import matplotlib.pyplot as plt

from pyresample.geometry import AreaDefinition
import cv2


def value_fun_light(color_array):
    return color_array[2]


def tifToJSON(area_definition, image, output_path, value_func, value_threshold):
    """converts an .tif satellite image to an JSON lat, lon, val object.
        Parameters
        ----------
        area_definition : AreaDefinition
            AreaDefinition to an .tif image area
            must be the same size as in area_definition declared (nonscaled)
        image : something after imread done
            File name of .tif image (extension included)
        output_path : string
            Path to which .json result is saved
        value_func : function
            function that converts pixel array (3 values) to value (0..1)
        value_threshold: double
            holds a threshold, value is written to a JSON only if greater
        """

    h, w, _ = image.shape
    lons, lats = area_definition.get_lonlats()
    jsonResult = []

    for y in range(h):
        for x in range(w):
            value = value_func(image[y, x])

            if value > value_threshold:
                jsonObj = {"val": value,
                           "lat": lats[y, x],
                           "lon": lons[y, x]}
                jsonResult.append(jsonObj)

# to file
    f = open(output_path + ".json", "w+")
    f.write(json.dumps(jsonResult))
    f.close()


area_BY = AreaDefinition(
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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    img = cv2.imread('night_overview.tif')

# do masking (work image out)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    cv2.fastNlMeansDenoisingColored(img, None, 20, 20, 7, 21)

    lower = np.array([28, 0, 50])  # temp solution
    upper = np.array([32, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    res = cv2.bitwise_and(img, img, mask=mask)
# cvt to json
    tifToJSON(area_definition=area_BY,
              image=res,
              output_path='result',
              value_func=value_fun_light,
              value_threshold= 120. / 255.)
    #
    # cv2.imwrite('night_overview_filtered.tif', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    # cv2.imwrite('night_overview_masked.tif', cv2.cvtColor(res, cv2.COLOR_RGB2BGR))
    # # cv2.imshow('mask', mask)
    # # cv2.imshow('res', res)
    # # cv2.waitKey()
    #
    # # _, axarr = plt.subplots(2, 2)
    # # axarr[0, 0].imshow(img)
    # # axarr[0, 1].imshow(mask)
    # # axarr[1, 0].imshow(res)
    # # plt.show()
    #
    # # size down image down by scale
    # scale = 2.0
    # scaledW = int(res.shape[1] / scale)
    # scaledH = int(res.shape[0] / scale)
    #
    # # resScaled = res.resize((scaledW, scaledH))
    # # hmapResScaled = hmap_res.resize((scaledW, scaledH))
    # # wri res
    # threshold = 120
    # hsvResScaled = cv2.cvtColor(res, cv2.COLOR_RGB2HSV)
    # jsonResult = []
    #
    # height, width, _ = res.shape
    # lons, lats = area_BY.get_lonlats()
    #
    # for y in range(height):
    #     for x in range(width):
    #         value = hsvResScaled[y, x][2]  # / 255
    #         valueNorm = value / 255
    #
    #         if value > threshold:
    #             hmap_res[y, x] = [value, value, value]
    #
    #             jsonObj = {"val": valueNorm,
    #                        "lat": lats[y, x],
    #                        "lon": lons[y, x]}
    #             jsonResult.append(jsonObj)
    #         else:
    #             hmap_res[y, x] = [0, 0, 0]
    #
    # cv2.imwrite('hmap.tif', hmap_res)
    # # to file
    # f = open("result.json", "w+")
    # f.write(json.dumps(jsonResult))
    # f.close()
