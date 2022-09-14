import json
import folium
import pandas
from folium.plugins import HeatMap

MINSK_LOCATION = [53.893009, 27.567444]

startmap = folium.Map(location=MINSK_LOCATION, zoom_start=9)


def MapGenerate(filename):
    map = startmap
    points = GetPoints('./map/backend/result.json')
    HeatMap(points, radius=10).add_to(map)
    map.save(filename)


def GetPoints(filename):
    file = open(filename)
    content = json.load(file)
    content = pandas.json_normalize(content)
    points = content[['lat', 'lon', 'val']]
    points.head()
    result = points.values.tolist()
    return result
