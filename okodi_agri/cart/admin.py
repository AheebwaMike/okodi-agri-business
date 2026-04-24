# okodi_agri/cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']
    fields = ['product', 'quantity', 'added_at']

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'item_count', 'total_value', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'item_count', 'total_value']
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Number of Items'
    
    def total_value(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_value.short_description = 'Cart Total'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_price.short_description = 'Total'

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
