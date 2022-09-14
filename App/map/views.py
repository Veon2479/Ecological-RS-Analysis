from django.shortcuts import render
from .backend import mapgenerate as mapgen

# Create your views here.

def index(request):
    mapgen.MapGenerate('./map/templates/map/index.html')
    return render(request, 'map/light.html')
