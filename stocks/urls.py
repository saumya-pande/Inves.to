from django.contrib import admin
from django.urls import path
from .views import fun, fun2

urlpatterns = [
    path('', fun),
    path('marketplace/', fun2 ),
    path('admin/', admin.site.urls),
]