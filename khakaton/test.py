import branca
import json
import folium
import requests
import pandas
from folium import plugins

m = folium.Map(location=[53.893009, 27.567444], zoom_start=10)

file = open('result.json')
points = json.load(file)

#plugins.HeatMap([[53.902284, 27.561831, 1]], name='sdffsdgsdfg', radius=100).add_to(m)

points = pandas.json_normalize(points)
stations = points[['lat', 'lon', 'val']]
stations.head()
stationArr = stations.values
plugins.HeatMap(stationArr, name='Light pollution', radius=10).add_to(m)
m.save("heat.html")




