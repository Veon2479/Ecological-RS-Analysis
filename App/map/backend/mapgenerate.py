import json
import folium
import pandas
import requests
import time

from folium import plugins
from folium.plugins import HeatMap
import numpy as np
from scipy.interpolate import griddata
import branca
import geojsoncontour
import matplotlib.pyplot as plt
import scipy as sp
import scipy.ndimage
import datetime

MINSK_LOCATION = [53.893009, 27.567444]

startmap = folium.Map(location=MINSK_LOCATION, zoom_start=9)


def MapGenerate(filename):
    map = folium.Map(location=MINSK_LOCATION, zoom_start=7)

    # Add the legend to the map
    plugins.Fullscreen(position='bottomright', force_separate_button=True).add_to(map)

    # Light pollution view generation
    light_pollution_group = folium.FeatureGroup(name="Light pollution", show=True)
    LightPollution(map).add_to(light_pollution_group)
    light_pollution_group.add_to(map)

    # Aerosol pollution view generation
    aerosol_pollution_group = folium.FeatureGroup(name="Aerosol pollution", show=False)
    aerosol_pollution_group.add_to(map)

    # Clouds pollution view generation
    clouds_pollution_group = folium.FeatureGroup(name="Clouds pollution", show=False)
    clouds_pollution_group.add_to(map)

    # ISS position view generation
    ISS_position_group = folium.FeatureGroup(name="ISS position", show=False)
    ISS(ISS_position_group)
    ISS_position_group.add_to(map)

    folium.LayerControl(position="bottomright").add_to(map)

    map.save(filename)
    return map


def GetPoints(filename):
    file = open(filename)
    content = json.load(file)
    content = pandas.json_normalize(content)
    points = content[['lat', 'lon', 'val']]
    points.head()
    result = points.values.tolist()
    return points


def ISS(map):
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
        if abs(line_points[i][1] - line_points[i + 1][1]) > 200:
            sections.append(i + 1)

    lines = np.split(line_points, indices_or_sections=sections)

    for line in lines:
        map.add_child(folium.PolyLine(locations=line))

    # Draw ISS markers
    for pos in positions:
        tip = datetime.datetime.fromtimestamp(int(pos['timestamp']))

        if pos['timestamp'] == positions[0]['timestamp']:
            icon = folium.features.CustomIcon("./map/static/map/img/ISS.png", icon_size=[30, 30])
        else:
            icon = folium.features.CustomIcon("./map/static/map/img/next.png", icon_size=[20, 20])

        map.add_child(folium.Marker(location=[pos['latitude'], pos['longitude']], icon=icon, popup="ISS", tooltip="Will be here at " + str(tip)))

def LightPollution(map):
    points = GetPoints('./map/backend/result.json')

    # Setup colormap
    colors = ['black', 'gray', 'blue', 'green', 'yellow', 'orange', 'red', 'brown']
    levels = len(colors)
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(levels)

    # Convertation to array
    x = points['lon'].tolist()
    y = points['lat'].tolist()
    z = points['val'].tolist()

    # Make a grid
    x_arr = np.linspace(np.min(x), np.max(x), 500)
    y_arr = np.linspace(np.min(y), np.max(y), 500)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

    # Grid the elevation (Edited on March 30th, 2020)
    z_mesh = griddata((x, y), z, (x_mesh, y_mesh), method='linear')

    # Use Gaussian filter to smoothen the contour
    sigma = [5, 5]
    z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    # Create the contour
    contourf = plt.contourf(x_mesh, y_mesh, z_mesh, levels, alpha=0.5, colors=colors, linestyles='solid', vmin=0, vmax=1)

    # Convert matplotlib contourf to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=5,
        stroke_width=1,
        fill_opacity=0.1)


    # Plot the contour on Folium map
    light_pollution_map = folium.GeoJson(
        geojson,
        style_function=lambda x: {
            'color': x['properties']['stroke'],
            'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'],
            'opacity': 0.5,
        })

    # Add the colormap to the folium map for legend
    cm.caption = 'Light pollution'
    map.add_child(cm)

    return light_pollution_map