from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.

def fun(request):

    return render(request, 'index.html' )

def fun2(request):
    context = {
        'index' : '/',
    }
    return render(request, 'market.html', context)