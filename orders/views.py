from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Order, Food, Beverage, OrderItem
from .forms import OrderForm



# Create your views here.

# View für die Bestellübersicht
def order_index(request):
    return render(request, 'orders/index.html', {'orders': Order.objects.all()})


# View für die Erstellung einer Bestellung
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('view_order', order_id=order.id)
    else:
        form = OrderForm()
    

    return render(request, 'orders/create_order.html', {'form': form})

def view_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    foods = Food.objects.all()
    beverages = Beverage.objects.all()
    return render(request, 'orders/view_order.html', {'order': order, 'order_items': order_items,'foods':foods, 'beverages':beverages})

def add_food_to_order(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        food_id = request.POST.get('food_id')
        quantity = request.POST.get('quantity')
        order_id = request.POST.get('order_id')

        order = Order.objects.get(id=order_id)
        food = Food.objects.get(id=food_id)
        price = food.price

        order_item = OrderItem.objects.create(food=food, quantity=quantity, price=price)
        order.items.add(order_item)

        order.total_price = order.total_price + price * int(quantity)
        order.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def add_beverage_to_order(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        beverage_id = request.POST.get('beverage_id')
        quantity = request.POST.get('quantity')
        order_id = request.POST.get('order_id')

        order = Order.objects.get(id=order_id)
        beverage = Beverage.objects.get(id=beverage_id)
        price = beverage.price

        order_item = OrderItem.objects.create(beverage=beverage, quantity=quantity, price=price)
        order.items.add(order_item)

        order.total_price += price * int(quantity)
        order.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def complete_order(request, order_id):
    if request.method == 'POST' and 'complete_order' in request.POST:
        order = Order.objects.get(id=order_id)
        # Zusätzliche Validierungen oder Geschäftslogik für die Bestellung durchführen, bevor sie gespeichert wird
        order.save()
        messages.success(request,'Bestellung erfolgreich aufgenommen.')
        return redirect('order_index')
    else:
        return redirect('order_view', order_id=order_id)