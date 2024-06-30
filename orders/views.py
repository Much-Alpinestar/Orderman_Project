import json
import logging
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Food, Beverage, OrderItem
from .forms import OrderForm

# View für die Bestellübersicht
def order_index(request):
    order_list = Order.objects.all().order_by('-created_at')  # Sortieren nach Erstellungsdatum
    paginator = Paginator(order_list, 10)  # 10 Bestellungen pro Seite

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'orders/index.html', {'page_obj': page_obj})


# View für die Erstellung einer Bestellung
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('edit_order', order_id=order.id)
    else:
        form = OrderForm()
    

    return render(request, 'orders/create_order.html', {'form': form})

def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/view_order.html', {'order': order, 'order_items': order_items})


def edit_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    foods = Food.objects.all()
    beverages = Beverage.objects.all()
    return render(request, 'orders/edit_order.html', {'order': order, 'order_items': order_items,'foods':foods, 'beverages':beverages})

def add_food_to_order(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        food_id = request.POST.get('food_id')
        quantity = int(request.POST.get('quantity'))
        order_id = request.POST.get('order_id')

        order = Order.objects.get(id=order_id)
        food = Food.objects.get(id=food_id)
        price = food.price

        if food.quantity >= quantity:
            order_item = OrderItem.objects.create(food=food, quantity=quantity, price=price)
            order.items.add(order_item)

            order.total_price = order.total_price + price * int(quantity)
            order.save()
            
            food.quantity -= quantity
            food.save()

            return JsonResponse({'success': True})
        else:
            message = f'Nicht genügend Bestand verfügbar. Nur {food.quantity} x {food.name} verfügbar.'
            
            return JsonResponse({'success': False, 'message': message})
    return JsonResponse({'success': False})

def add_beverage_to_order(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        beverage_id = request.POST.get('beverage_id')
        quantity = int(request.POST.get('quantity'))
        order_id = request.POST.get('order_id')

        order = Order.objects.get(id=order_id)
        beverage = Beverage.objects.get(id=beverage_id)
        price = beverage.price

        if beverage.quantity >= quantity:
            order_item = OrderItem.objects.create(beverage=beverage, quantity=quantity, price=price)
            order.items.add(order_item)

            order.total_price += price * int(quantity)
            order.save()
            
            beverage.quantity -= quantity
            beverage.save()

            return JsonResponse({'success': True})
        else:
            message = f'Nicht genügend Bestand verfügbar. Nur {beverage.quantity} x {beverage.name} verfügbar.'
            return JsonResponse({'success': False, 'message':message})
    return JsonResponse({'success': False})

def complete_order(request, order_id):
    if request.method == 'POST' and 'complete_order' in request.POST:
        order = Order.objects.get(id=order_id)
        # Zusätzliche Validierungen oder Geschäftslogik für die Bestellung durchführen, bevor sie gespeichert wird
        order.save()
        messages.success(request,'Bestellung erfolgreich aktualisiert.')
        return redirect('order_index')
    else:
        return redirect('order_view', order_id=order_id)
      
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    unpaid_items = order.items.filter(paid=False)
    paid_items = order.items.filter(paid=True)
    
    # Filter unpaid_items to exclude items with no remaining quantity to be paid
    unpaid_items = unpaid_items.annotate(remaining_quantity=models.F('quantity') - models.F('paid_quantity')).filter(remaining_quantity__gt=0)
    
    unpaid_total = sum(item.price * item.quantity for item in unpaid_items)
    paid_total = sum(item.price * item.quantity for item in paid_items)
    
    return render(request, 'orders/order_summary.html', {
        'order': order,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'unpaid_total': unpaid_total,
        'paid_total': paid_total
    })


@csrf_exempt
def calculate_split(request, order_id):
    if request.method == 'POST':
        try:
            item_ids = json.loads(request.POST.get('item_ids', '[]'))
            quantities = json.loads(request.POST.get('quantities', '[]'))

            item_ids = [int(i) for i in item_ids]
            quantities = [int(q) for q in quantities]

            items = OrderItem.objects.filter(id__in=item_ids)
            
            split_total = 0
            for item, quantity in zip(items, quantities):
                split_total += item.price * quantity

            return JsonResponse({'success': True, 'split_total': split_total})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})


logger = logging.getLogger(__name__)

@csrf_exempt
def mark_items_as_paid(request, order_id):
    if request.method == 'POST':
        try:
            item_ids = json.loads(request.POST.get('item_ids', '[]'))
            quantities = json.loads(request.POST.get('quantities', '[]'))
            
            item_ids = [int(i) for i in item_ids]
            items = OrderItem.objects.filter(id__in=item_ids)
            
            for item, quantity in zip(items, quantities):
                quantity = int(quantity)
                item.paid_quantity += quantity
                if item.paid_quantity >= item.quantity:
                    item.paid = True
                item.save()
            
            order = Order.objects.get(id=order_id)
            if not order.items.filter(paid=False).exists():
                order.paid = True
                order.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})


def mark_order_as_paid(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.items.update(paid=True, paid_quantity=models.F('quantity'))
        order.paid = True
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def check_all_items_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    all_items_paid = not order.items.filter(paid=False).exists()
    return JsonResponse({'all_items_paid': all_items_paid})