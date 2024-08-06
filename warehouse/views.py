from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages

from .forms import BeverageQuantityForm, FoodForm, BeverageForm, FoodQuantityForm
from .models import Food, Beverage, Item

# Create your views here.
@login_required
@permission_required('warehouse.view_food', 'warehouse.view_beverage')
def index(request):
    foods = Food.objects.filter(is_active=True)
    beverages = Beverage.objects.filter(is_active=True)
    return render(request, 'warehouse/index.html', {
        'foods':foods, 
        'beverages':beverages
    })

@login_required
@permission_required('warehouse.view_item')
def view_item(request, category_id, item_id):
    # Hole die Kategorie anhand der übergebenen ID
    category = get_object_or_404(Item, pk=category_id)

    # Prüfe, ob die Kategorie gültig ist
    if category.name in ['Food', 'Beverages']:
        # Bestimme die entsprechende Modelklasse basierend auf der Kategorie
        item_model = Food if category.name == 'Food' else Beverage
        
        # Hole das Item-Objekt basierend auf der Modelklasse und der übergebenen ID
        item = get_object_or_404(item_model, pk=item_id)
        
        return HttpResponseRedirect(reverse('index'))
    else:
        # Behandlung für ungültige Kategorie
        return HttpResponse('Invalid category')

@login_required
@permission_required('warehouse.add_food')
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Die Speise wurde erfolgreich hinzugefügt.')
            return redirect('index')
    else:
        form = FoodForm()
    return render(request, 'warehouse/add_food.html', {'form':form})

@login_required
@permission_required('warehouse.add_beverage')
def add_beverage(request):
    if request.method == 'POST':
        form = BeverageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Das Getränk wurde erfolgreich hinzugefügt')
            return redirect('index')
    else:
        form = BeverageForm()
    return render(request, 'warehouse/add_beverage.html',{'form':form})

@login_required
@permission_required('warehouse.change_food')           
def edit_food(request, food_id):
    food_instance = get_object_or_404(Food, id=food_id)
    
    if request.method == 'POST':
        form = FoodQuantityForm(request.POST, instance=food_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Die Speise wurde erfolgreich geändert.')
            return redirect('index')
    else:
        form = FoodQuantityForm(instance=food_instance)
    
    return render(request, 'warehouse/edit_food.html', {'form': form})

@login_required
@permission_required('warehouse.change_beverage')
def edit_beverage(request, beverage_id):
    beverage_instance = get_object_or_404(Beverage, id=beverage_id)

    if request.method == 'POST':
        form = BeverageQuantityForm(request.POST, instance=beverage_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Das Getränk wurde erfolgreich geändert.')
            return redirect('index')
    else:
        form = BeverageQuantityForm(instance=beverage_instance)

    return render(request, 'warehouse/edit_beverage.html', {'form':form})

@login_required
@permission_required('warehouse.delete_food')
def delete_food(request, food_id):
    food_instance = get_object_or_404(Food, id=food_id)
    food_instance.delete()
    messages.success(request, 'Die Speise wurde erfolgreich gelöscht.')
    return redirect('index')

@login_required
@permission_required('warehouse.delete_beverage')
def delete_beverage(request, beverage_id):
    beverage_instance = get_object_or_404(Beverage, id=beverage_id)
    beverage_instance.delete()
    messages.success(request, 'Das Getränk wurde erfolgreich gelöscht.')
    return redirect('index')

@login_required
@permission_required('warehouse.change_food')
def remove_food_from_stock(request, food_id):
    food_instance = get_object_or_404(Food, pk=food_id)
    food_instance.is_active = False
    food_instance.save()
    messages.success(request, 'Die Speise wurde aus dem Lager entfernt')
    return redirect('index')

@login_required
@permission_required('warehouse.change_beverage')
def remove_beverage_from_stock(request, beverage_id):
    beverage_instance = get_object_or_404(Beverage, pk=beverage_id)
    beverage_instance.is_active = False
    beverage_instance.save()
    messages.success(request, 'Das Getränk wurde aus dem Lager entfernt')
    return redirect('index')