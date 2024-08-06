from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>', views.view_item, name='view_item'),
    path('add_food/', views.add_food, name='add_food'),
    path('add_beverage/', views.add_beverage, name='add_beverage'),
    path('edit_food/<int:food_id>', views.edit_food, name='edit_food'),
    path('edit_beverage/<int:beverage_id>',views.edit_beverage, name='edit_beverage'),
    path('delete_food/<int:food_id>', views.delete_food, name='delete_food'),
    path('delete_beverage/<int:beverage_id>', views.delete_beverage, name='delete_beverage'),
    path('food/remove/<int:food_id>/', views.remove_food_from_stock, name='remove_food_from_stock'),
    path('beverage/remove/<int:beverage_id>/', views.remove_beverage_from_stock, name='remove_beverage_from_stock'),
]