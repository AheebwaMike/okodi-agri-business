# okodi_agri/cart/admin.py

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']
    fields = ['product_link', 'quantity', 'added_at']
    
    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'item_count', 'total_value', 'created_at', 'status_badge']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at', 'item_count', 'total_value']
    inlines = [CartItemInline]
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return f"Session: {obj.session_key[:10]}..."
    user_link.short_description = 'User/Session'
    
    def item_count(self, obj):
        count = obj.items.count()
        if count > 0:
            return format_html('<span style="color: #ff9800; font-weight: bold;">{}</span>', count)
        return 0
    item_count.short_description = 'Items'
    
    def total_value(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_value.short_description = 'Cart Total'
    
    def status_badge(self, obj):
        if obj.items.count() > 0:
            return format_html('<span style="color: #4caf50;">🛒 Active</span>')
        return "Empty"
    status_badge.short_description = 'Status'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart_link', 'product_link', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['total_price']
    
    def cart_link(self, obj):
        if obj.cart.user:
            return format_html('{}', obj.cart.user.username)
        return f"Session: {obj.cart.session_key[:10]}..."
    cart_link.short_description = 'User'
    
    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def total_price(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_price.short_description = 'Total'