
import numpy as np
import json
import matplotlib.pyplot as plt
from pyresample.geometry import AreaDefinition
import cv2
from pathlib import Path
from glob import glob
import config
import os

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

if __name__ == '__main__':
    inTifResultDir = Path(config.resultTiff)
    inTifResultDir.mkdir(parents=True, exist_ok=True)
    outJSONResultDir = Path(config.resultTiff)
    outJSONResultDir.mkdir(parents=True, exist_ok=True)
    tifDirs = glob(str(inTifResultDir) + '/**/')
    for tifDir in tifDirs:
        tifDirName = os.path.dirname(tifDir)
        tifDirName = os.path.basename(tifDirName)
        outJSONResultDir = Path(config.resultJSON + tifDirName)
        outJSONResultDir.mkdir(parents=True, exist_ok=True)
        tifFiles = glob(tifDir + '/*.tif')
        for tifFile in tifFiles:
            outJSONResultDir = Path(config.resultJSON + tifDirName)
            outJSONResultDir = outJSONResultDir / os.path.splitext(os.path.basename(tifFile))[0]
            outJSONResultDir.mkdir(parents=True, exist_ok=True)
            outJSONResultDirName = str(outJSONResultDir) + '/'
            img = cv2.imread(tifFile)

            hmap_res = img.copy()  # TEST

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

            cv2.fastNlMeansDenoisingColored(img, None, 20, 20, 7, 21)

            lower = np.array([28, 0, 50])  # temp solution
            upper = np.array([32, 255, 255])

            mask = cv2.inRange(hsv, lower, upper)
            res = cv2.bitwise_and(img, img, mask=mask)

            cv2.imwrite(outJSONResultDirName + '_filtered.tif', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(outJSONResultDirName + '_masked.tif', cv2.cvtColor(res, cv2.COLOR_RGB2BGR))

            scale = 2.0
            scaledW = int(res.shape[1] / scale)
            scaledH = int(res.shape[0] / scale)

            threshold = 120
            hsvResScaled = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) #res
            jsonResult = []

            height, width, _ = res.shape
            lons, lats = area_BY.get_lonlats()

            for y in range(height):
                for x in range(width):
                    value = hsvResScaled[y, x][2]  # / 255
                    valueNorm = value / 255

                    if value > threshold:
                        hmap_res[y, x] = [value, value, value]

                        jsonObj = {"val": valueNorm,
                                   "lat": lats[y, x],
                                   "lon": lons[y, x]}
                        jsonResult.append(jsonObj)
                    else:
                        hmap_res[y, x] = [0, 0, 0]

            cv2.imwrite(outJSONResultDirName + '_hmap.tif', hmap_res)
            f = open(outJSONResultDirName + "_result.json", "w+")
            f.write(json.dumps(jsonResult))
            f.close()
            print('Done: ' + os.path.dirname(outJSONResultDirName))
