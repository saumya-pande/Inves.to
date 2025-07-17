from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Stocks, UserInfo, UserStock
from django.core.paginator import Paginator
import threading
import json
import requests
# Create your views here.

def send_email_async(subject, message, from_email, recipient_list):
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, fail_silently=False)

def home_view(request):
    if request.user.is_authenticated:
        try:
            user_info = UserInfo.objects.get(user=request.user)
            user_stocks = UserStock.objects.filter(user=user_info)
            
            # Calculate dashboard data
            data = []
            total_invested = 0
            total_current_value = 0
            
            for user_stock in user_stocks:
                current_value = user_stock.purchase_quantity * user_stock.stock.curr_price
                total_invested += user_stock.purchase_quantity * user_stock.purchase_price
                total_current_value += current_value
                
                data.append({
                    'stock': user_stock.stock,
                    'purchase_price': user_stock.purchase_price,
                    'purchase_quantity': user_stock.purchase_quantity,
                    'total_value': current_value
                })
            
            # Calculate gains percentage
            gains_percentage = 0
            if total_invested > 0:
                gains_percentage = ((total_current_value - total_invested) / total_invested) * 100
            
            context = {
                'data': data,
                'invested': total_invested,
                'total_value': total_current_value,
                'gains': round(gains_percentage, 2)
            }
        except UserInfo.DoesNotExist:
            context = {
                'data': [],
                'invested': 0,
                'total_value': 0,
                'gains': 0
            }
    else:
        context = {}
    
    return render(request, 'index.html', context)

def redirect_to_home(request):
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

def market_view(request):
    # search
    q = request.GET.get('q')
    if q:
        stock_list = Stocks.objects.filter(name__icontains=q)
    else:
        stock_list = Stocks.objects.all()

    paginator = Paginator(stock_list, 9)
    page_number = request.GET.get('p')
    page_obj = paginator.get_page(page_number)
    
    # Get user holdings for sell validation
    user_holdings = {}
    if request.user.is_authenticated:
        try:
            user_info = UserInfo.objects.get(user=request.user)
            user_stocks = UserStock.objects.filter(user=user_info)
            for user_stock in user_stocks:
                user_holdings[user_stock.stock.id] = user_stock.purchase_quantity
        except UserInfo.DoesNotExist:
            # User doesn't have UserInfo record yet
            user_holdings = {}
    
    context = {
        'stocks': page_obj,
        'query': q,
        'user_holdings': json.dumps(user_holdings),
    }
    return render(request, 'market.html', context)

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


def logout_view(request) :
    logout(request)
    return redirect('index')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        address = request.POST.get('address')
        pan_card = request.POST.get('pan_card')
        phone_number = request.POST.get('phone_number')
        pan_image = request.FILES.get('pan_image')
        user_image = request.FILES.get('user_image')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Try again")
            return render(request, 'register.html')

        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        print(user_image)
        #saving to the database
        user_info = UserInfo(
            user=user,
            pancard_number=pan_card,
            address=address,
            phone_number=phone_number,
            user_image=user_image,
            pancard_image=pan_image,
        )
        user_info.save()

        login(request, user)
        return redirect('index')

    return render(request, 'register.html')

@login_required
def buy(request, id):
    stock = get_object_or_404(Stocks, id=id)
    
    # Get or create UserInfo for the user
    try:
        user_info = UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
        # Create UserInfo record if it doesn't exist
        user_info = UserInfo.objects.create(
            user=request.user,
            pancard_number="",
            address="",
            phone_number=""
        )
    
    purchase_quantity = int(request.POST.get('quantity'))
    purchase_price = float(request.POST.get('real-time-price') or stock.curr_price)
    print(f"Buying {purchase_quantity} shares of {stock.name} at ₹{purchase_price}")

    userStocks = UserStock.objects.filter(stock=stock, user=user_info).first()
    if userStocks:
        userStocks.purchase_price = (userStocks.purchase_quantity*userStocks.purchase_price + purchase_price*purchase_quantity) / (purchase_quantity + userStocks.purchase_quantity)
        userStocks.purchase_quantity = userStocks.purchase_quantity + purchase_quantity
        userStocks.save()
    else:
        userStock = UserStock(stock=stock, user=user_info, purchase_price=purchase_price, purchase_quantity=purchase_quantity)
        userStock.save()

    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Buy Option executed successfully",
            "message": f"Your purchase of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [request.user.email],
        }
    )
    t1.start()
    return redirect('index')

@login_required
def sell(request, id):
    stock = get_object_or_404(Stocks, id=id)
    
    # Get or create UserInfo for the user
    try:
        user_info = UserInfo.objects.get(user=request.user)
    except UserInfo.DoesNotExist:
        # Create UserInfo record if it doesn't exist
        user_info = UserInfo.objects.create(
            user=request.user,
            pancard_number="",
            address="",
            phone_number=""
        )
    
    sell_quantity = int(request.POST.get('quantity'))
    userStock = UserStock.objects.filter(stock=stock, user=user_info).first()

    if not userStock or userStock.purchase_quantity < sell_quantity:
        messages.error(request, "Can't sell more than you own")
        return redirect('market')

    userStock.purchase_quantity -= sell_quantity
    userStock.save()
    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Sell Option executed successfully",
            "message": f"Your sale of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [request.user.email],
        }
    )
    t1.start()

    return redirect('index')


# select  * from  student where marks > 60

