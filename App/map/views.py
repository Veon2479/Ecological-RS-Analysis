from django.shortcuts import render
from .backend import mapgenerate as mapgen
from django.http import HttpResponse

# Create your views here.

def index(request):
    mapgen.MapGenerate('./map/templates/map/index.html')
    return render(request, 'map/light.html')

def star(request):
    return HttpResponse("<h1>star</h1>")