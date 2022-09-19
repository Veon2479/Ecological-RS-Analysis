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
    lat = request.GET.get("lat", MINSK_LOCATION[0])
    lon = request.GET.get("lon", MINSK_LOCATION[1])
    if (not lat.isdigit()) or (not lon.isdigit()):
        lat = MINSK_LOCATION[0]
        lon = MINSK_LOCATION[1]
    path = starmapgen(lat, lon, './map/templates/starmap/index.html')
    path = '/starmap/example.jpg'
    data = {"lat": lat, "lon": lon, "path": path}
    return render(request, 'starmap/starmap.html', data)
