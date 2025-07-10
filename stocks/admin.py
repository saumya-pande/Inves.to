from django.contrib import admin

from .models import Stocks, UserInfo, UserStock

# Register your models here.
admin.site.register(Stocks)
admin.site.register(UserInfo)
admin.site.register(UserStock)