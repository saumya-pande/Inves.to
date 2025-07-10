from django.contrib import admin
from django.urls import path
from .views import home_view, get_data, market_view, login_view, register_view, logout_view, buy, sell
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home_view, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('fetchData/', get_data, name='fetchData' ),
    path('market/', market_view, name='market' ),
    path('logout/' ,  logout_view , name = 'logout'),
    path('buy/<int:id>/', buy, name='buy'),
    path('sell/<int:id>/', sell, name='sell'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
