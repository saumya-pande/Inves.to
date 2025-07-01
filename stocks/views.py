from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import Stocks
# Create your views here.
import requests

def fun(request):

    return render(request, 'index.html' )

def fun2(request):
    context = {
        'index' : '/',
    }
    return render(request, 'market.html', context)


def get_data(request):
    headers = {
        'Content-Type': 'application/json'
    }

    token = 'ee9169d5e062546643314acf23639685734a15e1'

    def get_stock_data(ticker):
        url = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={token}"
        priceurl = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"
        requestResponse = requests.get(url, headers=headers)
        Metadata = requestResponse.json()
        print(Metadata)
        pricedata = requests.get(priceurl, headers=headers)
        print(pricedata.json())
        pricedata = pricedata.json()[0]['close']

        stock = Stocks(ticker=Metadata['ticker'], name=Metadata['name'], description=Metadata['description'], curr_price=pricedata)
        stock.save()

    tickers = [
            "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "AMD", "NFLX", "INTC",
            "ADBE", "PDD", "COST", "AVGO", "QCOM", "PYPL", "CMCSA", "CSCO", "MARA", "RIVN"
        ]
    for i in tickers:
            get_stock_data(i)

    return JsonResponse({"status": "stocks updated"})

@login_required
def stocks(request) :
    stocks  = Stocks.objects.all()
    context  =  {'data' :  stocks}
    return render(request , 'market.html' ,  context)


def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


def logoutView(request) :
    logout(request)
    return redirect('login')