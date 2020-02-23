from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def validation_key(request, key):
    return render(request, 'index.html')

