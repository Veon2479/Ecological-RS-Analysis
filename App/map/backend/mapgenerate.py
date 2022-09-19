import json
from collections.abc import Iterable
import folium
import pandas
import requests
import time
from branca.element import MacroElement
from folium import plugins
import numpy as np
from folium.plugins import MousePosition
from jinja2 import Template
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
    formatter = "function(num) {return L.Util.formatNum(num, 6) + ' º ' ;};"
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

    m.add_child(LatLngPopup())


    # Light pollution view generation
    light_pollution_group = folium.FeatureGroup(name="Light pollution", show=True)
    color_legend = LightPollution(light_pollution_group)
    m.add_child(color_legend)
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

def LightPollution(light_pollution_map):

    # Load points data
    points = md.get_param('night_overview')
    res = np.split(points, [1, 2, 3], axis=1)
    x = list(flatten(res[1]))
    y = list(flatten(res[0]))
    z = list(flatten(res[2]))

    # Setup colormap
    colors = ['black', 'gray', 'blue', 'green', 'yellow', 'orange', 'red', 'brown']
    levels = len(colors)
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(levels)

    # Make a grid
    x_arr = np.linspace(np.min(x), np.max(x), 700)
    y_arr = np.linspace(np.min(y), np.max(y), 700)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

    # Grid the elevation
    z_mesh = griddata((x, y), z, (x_mesh, y_mesh), method='linear')

    # Use Gaussian filter to smoothen the contour
    sigma = [5, 5]
    z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    # Create the contour
    contourf = plt.contourf(x_mesh, y_mesh, z_mesh, levels, alpha=0.5, colors=colors, linestyles='None', vmin=0,
                            vmax=1)
    # Convert matplotlib contourf to geojson
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=5,
        stroke_width=1,
        fill_opacity=0.1)

    # Plot the contour on Folium map
    m = folium.features.GeoJson(
        geojson,
        style_function=lambda x: {
            'color': x['properties']['stroke'],
            'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'],
            'opacity': 0.5,
       })

    # Add the colormap to the folium map for legend
    cm.caption = 'Light pollution'

    light_pollution_map.add_child(m)

    return cm

    #light_pollution_map.add_child(folium.plugins.HeatMap(points, radius=10))

def ISS(ISS_map):
    path = "https://api.wheretheiss.at/v1/satellites/25544/positions?timestamps="
    timestamp = int(time.time())

    for i in range(1, 15):
        path += str(timestamp) + ","
        timestamp += 450

    path = path[:-1]

    try:
        response = requests.get(path)
        if response.status_code != 200:
            return
    except:
        return

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
            ISS_map.add_child(
                folium.Marker(location=[pos['latitude'], pos['longitude']], icon=icon, popup=tip, tooltip=tooltip))
        else:
            ISS_map.add_child(
                folium.CircleMarker(location=[pos['latitude'], pos['longitude']], color="blue", fill_color="Blue",
                                    radius=7, popup=tip, tooltip=tooltip))

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

class LatLngPopup(MacroElement):
    """
    When one clicks on a Map that contains a LatLngPopup,
    a popup is shown that displays the latitude and longitude of the pointer.
    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Latitude: " + e.latlng.lat.toFixed(4) +
                                    "<br>Longitude: " + e.latlng.lng.toFixed(4) + 
                                    "<br>View the star map " + "<a href=\\"/starmap?lat=" + e.latlng.lat + "&lon=" + e.latlng.lng + "\\">here</a>")
                        .openOn({{this._parent.get_name()}});
                    parent.document.getElementById("id_lng").value = e.latlng.lng.toFixed(4);
                    parent.document.getElementById("id_lat").value = e.latlng.lat.toFixed(4);
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
            """)  # noqa

    def __init__(self):
        super(LatLngPopup, self).__init__()
        self._name = 'LatLngPopup'