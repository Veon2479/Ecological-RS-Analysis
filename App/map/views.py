from django.shortcuts import render
from .backend import mapgenerate as mapgen
<<<<<<< HEAD
from django.http import HttpResponse
=======
from .backend.starmap_generate import map_generate as starmapgen
from .backend.mapgenerate import MINSK_LOCATION

>>>>>>> f75b0ef7b08b2b874189f57da0bfd39613f43c0f

# Create your views here.

def index(request):
    mapgen.MapGenerate('./map/templates/map/index.html')
    return render(request, 'map/light.html')

<<<<<<< HEAD
def star(request):
    return HttpResponse("<h1>star</h1>")
=======

def starmap(request):
    # lat = request.GET.get('lat', MINSK_LOCATION[0])
    # lon = request.Get.get('lon', MINSK_LOCATION[1])
    lat = request.GET['lat']
    lon = request.GET['lon']
    if (not isinstance(lat, float)) or (not isinstance(lon, float)):
        lat = MINSK_LOCATION[0]
        lon = MINSK_LOCATION[1]
    path = starmapgen(lat, lon, './map/templates/starmap/index.html')
    # path = '/starmap/example.jpg'
    data = {"lat": lat, "lon": lon, "path": path}
    return render(request, 'starmap/starmap.html', data)
>>>>>>> f75b0ef7b08b2b874189f57da0bfd39613f43c0f
