from django.shortcuts import render

def handler404(request, exception):
    return render(request, 'home/error.html')
