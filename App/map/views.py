from django.shortcuts import render
from .backend import mapgenerate as mapgen
from django.http import HttpResponse
from .backend.starmap_generate import map_generate as starmapgen
from .backend.mapgenerate import MINSK_LOCATION


# Create your views here.

def map(request):
    mapgen.MapGenerate('./map/templates/map/index.html')
    return render(request, 'map/light.html')


def starmap(request):
    lat = 0.0
    lon = 0.0
    try:
        lat = request.GET.get("lat", MINSK_LOCATION[0])
        lon = request.GET.get("lon", MINSK_LOCATION[1])
    finally:
        if (not is_float(lat)) or (not is_float(lon)):
            lat = MINSK_LOCATION[0]
            lon = MINSK_LOCATION[1]
    path = starmapgen(lat, lon, './map/templates/starmap/index.html')
    path = '/starmap/example.jpg'
    data = {"lat": lat, "lon": lon, "path": path}
    return render(request, 'starmap/starmap.html', data)


def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
