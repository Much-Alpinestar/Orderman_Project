from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_index, name='order_index'),
    path('create_order/', views.create_order, name='create_order'),
    path('order/<int:order_id>/', views.view_order, name='view_order'),
    path('order/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    
    #path('view_order/<int:order_id>', views.view_order, name='view_order'),
    path('add_food_to_order',views.add_food_to_order, name='add_food_to_order'),
    path('add_beverage_to_order', views.add_beverage_to_order, name='add_beverage_to_order'),
    
    path('complete_order/<int:order_id>', views.complete_order, name='complete_order'),
    path('order/<int:order_id>/summary/', views.order_summary, name='order_summary'),
    path('order/<int:order_id>/mark_items_as_paid/', views.mark_items_as_paid, name='mark_items_as_paid'),
    path('order/<int:order_id>/calculate_split/', views.calculate_split, name='calculate_split'),
    path('order/<int:order_id>/mark_as_paid/', views.mark_order_as_paid, name='mark_order_as_paid'),
    path('order/<int:order_id>/check_all_items_paid/', views.check_all_items_paid, name='check_all_items_paid'),
]