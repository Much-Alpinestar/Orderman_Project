from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_index, name='order_index'),
    path('create_order/', views.create_order, name='create_order'),
    path('view_order/<int:order_id>', views.view_order, name='view_order'),
    path('add_food_to_order',views.add_food_to_order, name='add_food_to_order'),
    path('add_beverage_to_order', views.add_beverage_to_order, name='add_beverage_to_order'),
    path('complete_order/<int:order_id>', views.complete_order, name='complete_order'),
]