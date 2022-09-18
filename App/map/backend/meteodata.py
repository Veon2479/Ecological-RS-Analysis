import numpy as np
import json

from pyresample.geometry import AreaDefinition
import cv2

SRC_PATH = './map/meteo_data/'

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


def value_fun_light(color_array):
    return color_array[2] / 255.


def do_masking_light(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([28, 0, 50])  # temp solution
    upper = np.array([32, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    return cv2.bitwise_and(hsv, hsv, mask=mask)


def tifToArray(area_definition, image, value_func, value_threshold):
    """converts an .tif satellite image to an JSON lat, lon, val object.
        Parameters
        ----------
        :param area_definition : AreaDefinition
            AreaDefinition to an .tif image area
            must be the same size as in area_definition declared (nonscaled)
        :param image : something after imread done
            File name of .tif image (extension included)
        :param value_func : function
            function that converts pixel array (3 values) to value (0..1)
        :param value_threshold: double
            holds a threshold, value is written to a JSON only if greater
        :return array [['lat', 'lon', 'val']]
        """

    h, w, _ = image.shape
    lons, lats = area_definition.get_lonlats()

    result = []

    for y in range(h):
        for x in range(w):
            value = value_func(image[y, x])

            if value > value_threshold:
                result.append([
                    lats[y, x],
                    lons[y, x],
                    value
                ])

                # jsonObj = {"val": value,
                #            "lat": lats[y, x],
                #            "lon": lons[y, x]}
                # jsonResult.append(jsonObj)

    return result

    # to file
    # f = open(output_path + ".json", "w+")
    # f.write(json.dumps(jsonResult))
    # f.close()


def get_param(param_name):
    """
    :param param_name : string
        'night_overview' -- returns light colors
    :return: array [['lat', 'lon', 'val']]
    """

    img = cv2.imread(SRC_PATH + param_name + '.tif')

    match param_name:
        case 'night_overview':
            # do masking (work image out)
            res_img = do_masking_light(img)
            # choose values
            func = value_fun_light
            value_threshold = 120. / 255.
        case _:
            return []

    # cvt to json
    return tifToArray(area_definition=area_BY,
                      image=res_img,
                      value_func=func,
                      value_threshold=value_threshold)


# (Example call)
if __name__ == "__main__":
    res = get_param('night_overview')

    for i in range(len(res)):
        print(res[i])
