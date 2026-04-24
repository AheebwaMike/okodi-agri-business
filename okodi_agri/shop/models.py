# okodi_agri/shop/models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

class Product(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Pricing and Stock
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Product Specifications
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Weight in kg', blank=True, null=True)
    measurement = models.CharField(max_length=100, blank=True, help_text='e.g., 5kg bag, 1 liter bottle, etc.')
    
    # Supplier/Farmer Information
    supplier_name = models.CharField(max_length=200, blank=True)
    supplier_location = models.CharField(max_length=200, blank=True)
    
    # Media
    main_image = models.ImageField(upload_to='products/main/', blank=True, null=True)
    additional_image_1 = models.ImageField(upload_to='products/additional/', blank=True, null=True)
    additional_image_2 = models.ImageField(upload_to='products/additional/', blank=True, null=True)
    additional_image_3 = models.ImageField(upload_to='products/additional/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Product Type (for filtering different agro products)
    PRODUCT_TYPES = [
        ('seeds', 'Seeds'),
        ('fertilizers', 'Fertilizers'),
        ('tools', 'Farm Tools'),
        ('livestock', 'Livestock'),
        ('fresh_produce', 'Fresh Produce'),
        ('processed', 'Processed Foods'),
        ('pesticides', 'Pesticides'),
        ('other', 'Other'),
    ]
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES, default='other')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])