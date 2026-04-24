# okodi_agri/orders/models.py

from django.db import models
from django.conf import settings
from shop.models import Product
from cart.models import Cart

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHODS = (
        ('cash', 'Cash on Delivery'),
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
    )
    
    # User information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    
    # Order details
    order_number = models.CharField(max_length=20, unique=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    
    # Shipping information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Delivery notes
    delivery_notes = models.TextField(blank=True)
    
    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD + timestamp + random number
            import random
            import time
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            self.order_number = f"ORD-{timestamp}-{random_num}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        return self.price * self.quantity
    