from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.IntegerField()
    category = models.CharField(max_length=100, default='Food')
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} - {self.quantity}x - {self.price}€"

class Food(Item):
    
    class Meta:
        verbose_name_plural = 'Food'   

class Beverage(Item):
    
    class Meta:
        verbose_name_plural = 'Beverages'
        
        