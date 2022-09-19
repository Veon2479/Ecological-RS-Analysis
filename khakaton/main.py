import numpy as np
import json

from pyresample.geometry import AreaDefinition
import cv2

import numpy as np
import json
import matplotlib.pyplot as plt
from pyresample.geometry import AreaDefinition
import cv2

import lightAnal as anal
import config as cfg


def do_masking_light(img):
    ifshift_mask = cv2.imread(cfg.FULL_PATH + 'testMask.tif', 0)
    ifshift_mask = ifshift_mask.astype(np.float32) / 255

    channel = img[:, :, 1]
    channel = anal.fft_filter(channel=channel, mask=ifshift_mask)
    result_img = np.dstack((channel, channel, channel))  # np.zeros((len(channel), len(channel[0])), dtype=np.uint8)

    return result_img


def tif_to_array(image, param):
    """converts an .tif satellite image to an JSON lat, lon, val object.
        Parameters
        ----------
        :param param : dict
            holds info needed according to parameters
        :param image : something after imread done
            File name of .tif image (extension included)
        :return array [['lat', 'lon', 'val']]
        """
    test_copy = image.copy()

    h, w, _ = image.shape
    lons, lats = cfg.area.get_lonlats()

    result = []
    for y in range(h):
        for x in range(w):
            value = param['value_func'](image[y, x])
            if value > param['threshold']:  # does it work on all data?
                result.append([
                    lats[y, x],
                    lons[y, x],
                    value
                ])
                test_copy[y, x] = [value*255, value*255, value*255]
            else:
                test_copy[y, x] = [0, 0, 0]

                # jsonObj = {"val": value,
                #            "lat": lats[y, x],
                #            "lon": lons[y, x]}
                # jsonResult.append(jsonObj)
    cv2.imwrite(cfg.FULL_PATH + param['name'] + '_ff' + cfg.EXT, test_copy)
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

    # get params
    param = cfg.parameters[param_name]
    # read image
    img = cv2.imread(cfg.FULL_PATH + param['name'] + cfg.EXT)
    # mask image out
    match param_name:
        case 'night_overview':
            # do masking (work image out)
            img = do_masking_light(img)

    # general masking
    mask = cv2.inRange(img, param['lower'], param['upper'])
    img = cv2.bitwise_and(img, img, mask=mask)
    # save temp mask and res
    cv2.imwrite(cfg.FULL_PATH + param['name'] + '_mask' + cfg.EXT, mask)
    cv2.imwrite(cfg.FULL_PATH + param['name'] + '_result' + cfg.EXT, img)
    # cvt to json
    return tif_to_array(img, param)


# (Example call)
if __name__ == "__main__":

    # res = get_param('night_overview')
    # res = get_param('fog')
    res = get_param('dust')

    for i in range(len(res)):
        print(res[i])
