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
    Light(light_pollution_group, m)
    m.add_child(light_pollution_group)

    # Clouds pollution view generation
    clouds_pollution_group = folium.FeatureGroup(name="Clouds pollution", show=False)
    Cloud(clouds_pollution_group, m)
    m.add_child(clouds_pollution_group)

    # Dust pollution view generation
    dust_pollution_group = folium.FeatureGroup(name="Dust pollution", show=False)
    Dust(dust_pollution_group, m)
    m.add_child(dust_pollution_group)

    # Fog pollution view generation
    fog_pollution_group = folium.FeatureGroup(name="Fog pollution", show=False)
    Fog(fog_pollution_group, m)
    m.add_child(fog_pollution_group)

    # ISS position view generation
    ISS_position_group = folium.FeatureGroup(name="ISS position", show=False)
    ISS(ISS_position_group)
    m.add_child(ISS_position_group)

    # Add layer control to the map
    folium.LayerControl(position="topright", sortLayers=True).add_to(m)

    m.save(filename)
    return m


def Light(light_pollution_map, map):
    # Load points data
    points = md.get_param('night_overview')
    x = points[1]
    y = points[0]
    z = points[2]

    # Setup colormap
    colors = ['black', 'gray', 'blue', 'green', 'yellow', 'orange', 'red', 'brown']
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(len(colors))
    cm.caption = 'Light pollution'

    gj = CreateGeoJson(x, y, z, colors)

    light_pollution_map.add_child(gj)
    map.add_child(cm)


def Cloud(cloud_pollution_map, map):
    # Load points data
    points = md.get_param('cloudtop')
    x = points[1]
    y = points[0]
    z = points[2]

    # Setup colormap
    colors = ['white', 'lightcyan', 'lightskyblue', 'skyblue', 'cornflowerblue', 'royalblue', 'blue', 'mediumblue', 'darkblue', 'indigo', 'darkmagenta']
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(len(colors))
    cm.caption = 'Clouds pollution'

    gj = CreateGeoJson(x, y, z, colors)
    cloud_pollution_map.add_child(gj)
    map.add_child(cm)


def Dust(dust_pollution_map, map):
    # Load points data
    points = md.get_param('dust')
    x = points[1]
    y = points[0]
    z = points[2]

    # Setup colormap
    colors = ['white', 'lemonchiffon', 'khaki', 'yellow', 'gold', 'orange', 'darkorange', 'orangered', 'red', 'firebrick', 'darkred']
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(len(colors))
    cm.caption = 'Dust pollution'

    gj = CreateGeoJson(x, y, z, colors)

    dust_pollution_map.add_child(gj)
    map.add_child(cm)


def Fog(fog_pollution_map, map):

    # Load points data
    points = md.get_param('fog')
    x = points[1]
    y = points[0]
    z = points[2]

    # Setup colormap
    colors = ['white', 'ghostwhite', 'thistle', 'plum', 'violet', 'm', 'fuchsia', 'magenta', 'orchid', 'purple', 'darkmagenta', 'indigo']
    cm = branca.colormap.LinearColormap(colors, vmin=0, vmax=1).to_step(len(colors))
    cm.caption = 'Fog pollution'

    gj = CreateGeoJson(x, y, z, colors)

    fog_pollution_map.add_child(gj)
    map.add_child(cm)

def CreateGeoJson(x, y, z, colors):
    levels = len(colors)

    # Make a grid
    x_arr = np.linspace(np.min(x), np.max(x), 500)
    y_arr = np.linspace(np.min(y), np.max(y), 500)
    x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

    # Grid the elevation
    z_mesh = griddata((x, y), z, (x_mesh, y_mesh), method='linear')

    # Use Gaussian filter to smoothen the contour
    sigma = [5, 5]
    z_mesh = sp.ndimage.filters.gaussian_filter(z_mesh, sigma, mode='constant')

    # Create the contour
    contourf = plt.contourf(x_mesh, y_mesh, z_mesh, levels, alpha=0.5, colors=colors, linestyles='None', vmin=0, vmax=1)
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

    return m



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
