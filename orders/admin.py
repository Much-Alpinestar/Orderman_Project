from django.contrib import admin
from .models import OrderTable, Order, OrderItem

# Register your models here.
admin.site.register(OrderTable)
admin.site.register(Order)
admin.site.register(OrderItem)

