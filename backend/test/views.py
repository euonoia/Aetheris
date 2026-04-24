from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def connection_test(request):
    # This data will be mapped in your React frontend
    data = [
        {"id": 1, "name": "Aetheris Backend: Online"},
        {"id": 2, "name": "App 'test': Active"},
        {"id": 3, "name": "Connection: Successful"},
    ]
    return JsonResponse(data, safe=False)