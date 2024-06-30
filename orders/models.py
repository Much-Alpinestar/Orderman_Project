from django.db import models

from warehouse.models import Beverage, Food

# Create your models here.
class OrderTable(models.Model):
    number_of_table = models.IntegerField(unique=True)

    def __str__(self):
        return f'Tisch {self.number_of_table}'
    
class Order(models.Model):
    table = models.ForeignKey(OrderTable, on_delete=models.CASCADE)
    items = models.ManyToManyField('OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.table}'
    

class OrderItem(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, blank=True)
    beverage = models.ForeignKey(Beverage, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_quantity = models.IntegerField(default=0)
    
    def __str__(self):
        if self.food:
            return f"{self.quantity}x {self.food.name} - {'Paid' if self.food.paid else 'Unpaid'}"
        elif self.beverage:
            return f"{self.quantity}x {self.beverage.name} - {'Paid' if self.beverage.paid else 'Unpaid'}"
        else:
            return "Invalid Order Item"
