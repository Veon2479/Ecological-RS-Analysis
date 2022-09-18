import json
import folium
import pandas
import requests
import time
from folium import plugins
import numpy as np
from folium.plugins import MousePosition
from scipy.interpolate import griddata
import branca
import geojsoncontour
import matplotlib.pyplot as plt
import scipy as sp
import scipy.ndimage
import datetime
from . import meteodata as md

MINSK_LOCATION = [53.893009, 27.567444]

startmap = folium.Map(location=MINSK_LOCATION, zoom_start=9)
def MapGenerate(filename):
    m = folium.Map(location=MINSK_LOCATION, zoom_start=7)

    # Add the full screen button to the map
    plugins.Fullscreen(position='bottomright', force_separate_button=True).add_to(m)

    # Add Mouse Position to get the coordinate (Lat, Long) for a mouse over on the map
    formatter = "function(num) {return L.Util.formatNum(num, 6);};"
    mouse_position = MousePosition(
        position='topright',
        separator=' Lon: ',
        empty_string='NaN',
        lng_first=False,
        num_digits=20,
        prefix='Lat:',
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(m)


    # Light pollution view generation
    light_pollution_group = folium.FeatureGroup(name="Light pollution", show=True)
    LightPollution(light_pollution_group)
    m.add_child(light_pollution_group)

    # Aerosol pollution view generation
    aerosol_pollution_group = folium.FeatureGroup(name="Aerosol pollution", show=False, control=True)
    m.add_child(aerosol_pollution_group)

    # Clouds pollution view generation
    clouds_pollution_group = folium.FeatureGroup(name="Clouds pollution", show=False)
    m.add_child(clouds_pollution_group)

    # ISS position view generation
    ISS_position_group = folium.FeatureGroup(name="ISS position", show=False)
    ISS(ISS_position_group)
    m.add_child(ISS_position_group)

    # Add layer control to the map
    folium.LayerControl(position="topright", sortLayers=True).add_to(m)

    m.save(filename)
    return m

def ISS(ISS_map):
    path = "https://api.wheretheiss.at/v1/satellites/25544/positions?timestamps="
    timestamp = int(time.time())

    for i in range(1, 15):
        path += str(timestamp) + ","
        timestamp += 450

    path = path[:-1]

    response = requests.get(path)
    positions = json.loads(response.text)

    # Draw line for ISS markers
    line_points = pandas.json_normalize(positions)
    line_points = line_points[['latitude', 'longitude']].values.tolist()

    sections = []

    for i in range(0, len(line_points) - 1):
        if abs(line_points[i][1] - line_points[i + 1][1]) > 180:
            sections.append(i + 1)

    lines = np.split(line_points, indices_or_sections=sections)

    for line in lines:
        ISS_map.add_child(folium.PolyLine(locations=line))

    # Draw ISS markers
    for pos in positions:
        ISS_time = datetime.datetime.fromtimestamp(int(pos['timestamp']))
        tooltip = "International Space Station"
        tip = "Will be here at " + str(ISS_time)

        if pos['timestamp'] == positions[0]['timestamp']:
            icon = folium.features.CustomIcon("./map/static/map/img/ISS.png", icon_size=[30, 30])
            ISS_map.add_child(folium.Marker(location=[pos['latitude'], pos['longitude']], icon=icon, popup=tip, tooltip=tooltip))
        else:
            ISS_map.add_child(folium.CircleMarker(location=[pos['latitude'], pos['longitude']], color="blue", fill_color="Blue", radius=7, popup=tip, tooltip=tooltip))


def LightPollution(light_pollution_map):
    points = md.get_param('night_overview')
    light_pollution_map.add_child(folium.plugins.HeatMap(points, radius=10))
