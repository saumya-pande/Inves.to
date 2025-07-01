from django.contrib import admin
from django.urls import path
from .views import fun, fun2, get_data

urlpatterns = [
    path('', fun),
    path('marketplace/', get_data ),
    path('admin/', admin.site.urls),
]