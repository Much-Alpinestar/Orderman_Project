import json
import logging
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models
from django.db.models import Case, When, IntegerField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Food, Beverage, OrderItem, Customer
from .forms import OrderForm

# View für die Bestellübersicht
@login_required
@permission_required('orders.view_order')
def order_index(request):
    order_list = Order.objects.annotate(
        is_paid=Case(
            When(paid=True, then=1),
            When(paid=False, then=0),
            output_field=models.IntegerField(),
        )
    ).order_by('is_paid', '-created_at')

    paginator = Paginator(order_list, 10)  # 10 Bestellungen pro Seite
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'orders/index.html', {'page_obj': page_obj})


# View für die Erstellung einer Bestellung
""" @login_required
@permission_required('orders.add_order')
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('edit_order', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form}) """

@login_required
@permission_required('orders.add_order')
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        customer_id = request.POST.get('customer_id')
        if form.is_valid() or customer_id:
            order = form.save(commit=False)
            if customer_id:
                order.customer = Customer.objects.get(id=customer_id)
                order.table = None
            if not order.table and not order.customer:
                form.add_error(None, 'Eine Bestellung muss entweder einen Tisch oder einen Kunden haben.')
            else:
                order.save()
                return redirect('edit_order', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})

@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            customer = Customer.objects.create(name=name)
            return JsonResponse({'success': True, 'customer': {'id': customer.id, 'name': customer.name}})
        else:
            return JsonResponse({'success': False, 'message': 'Alle Felder müssen ausgefüllt sein.'})
    return JsonResponse({'success': False, 'message': 'Ungültige Anfrage.'})

@login_required
@permission_required('orders.view_order')
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    for item in order_items:
        item.total_price = item.price * item.quantity

    return render(request, 'orders/view_order.html', {'order': order, 'order_items': order_items})

@login_required
@permission_required('orders.change_order')
def edit_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    foods = Food.objects.all()
    beverages = Beverage.objects.all()

    for item in order_items:
        item.total_price = item.price * item.quantity

    return render(request, 'orders/edit_order.html', {'order': order, 'order_items': order_items,'foods':foods, 'beverages':beverages})

@login_required
@permission_required('orders.add_orderitem')
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

@login_required
@permission_required('orders.add_orderitem')
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

@login_required
@permission_required('orders.change_order')
def complete_order(request, order_id):
    if request.method == 'POST' and 'complete_order' in request.POST:
        order = Order.objects.get(id=order_id)
        # Zusätzliche Validierungen oder Geschäftslogik für die Bestellung durchführen, bevor sie gespeichert wird
        order.save()
        messages.success(request,'Bestellung erfolgreich aktualisiert.')
        return redirect('order_index')
    else:
        return redirect('order_view', order_id=order_id)

@login_required
@permission_required('orders.view_order')      
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    unpaid_items = order.items.filter(paid=False)
    paid_items = order.items.filter(paid=True)
    
    unpaid_items = [
        {
            'id': item.id,
            'food': item.food,
            'beverage': item.beverage,
            'price': item.price,
            'quantity': item.quantity,
            'paid_quantity': item.paid_quantity,
            'remaining_quantity': item.quantity - item.paid_quantity,
            'total_price': item.price * item.quantity
        }
        for item in unpaid_items
    ]
    
    unpaid_total = sum(item['price'] * item['quantity'] for item in unpaid_items)
    paid_total = sum(item.price * item.quantity for item in paid_items)
    
    return render(request, 'orders/order_summary.html', {
        'order': order,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'unpaid_total': unpaid_total,
        'paid_total': paid_total
    })

@login_required
@permission_required('orders.change_orderitem')
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

@login_required
@permission_required('orders.change_orderitem')
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

@login_required
@permission_required('orders.change_order')
def mark_order_as_paid(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.items.update(paid=True, paid_quantity=models.F('quantity'))
        order.paid = True
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@permission_required('orders.view_order')
def check_all_items_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    all_items_paid = not order.items.filter(paid=False).exists()
    return JsonResponse({'all_items_paid': all_items_paid})

@login_required
@permission_required('orders.can_cancel_order')
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.canceled = True
    order.save()

    # Restock items
    for item in order.items.all():
        if item.food:
            item.food.quantity += item.quantity
            item.food.save()
        if item.beverage:
            item.beverage.quantity += item.quantity
            item.beverage.save()

    messages.success(request, 'Die Bestellung wurde erfolgreich storniert.')
    return redirect('order_index')