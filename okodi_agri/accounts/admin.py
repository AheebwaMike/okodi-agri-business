from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django.db import models
from orders.models import Order
from cart.models import Cart

class OrderInline(admin.TabularInline):
    model = Order
    fields = ['order_number', 'status', 'total_amount', 'created_at', 'view_link']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'view_link']
    extra = 0
    can_delete = False
    show_change_link = False
    max_num = 10
    
    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:orders_order_change', args=[obj.pk])
            return format_html('<a href="{}">View Order</a>', url)
        return "-"
    view_link.short_description = 'Details'

class CartInline(admin.TabularInline):
    model = Cart
    fields = ['cart_items', 'total_value', 'created_at']
    readonly_fields = ['cart_items', 'total_value', 'created_at']
    extra = 0
    can_delete = False
    max_num = 1
    
    def cart_items(self, obj):
        items = obj.items.all()
        if items:
            return format_html('<br>'.join([f'{item.quantity} x {item.product.name}' for item in items[:5]]))
        return "Empty cart"
    cart_items.short_description = 'Cart Items'
    
    def total_value(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_value.short_description = 'Cart Total'

class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'order_count', 'cart_status', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Add computed fields to readonly_fields so they can be used in fieldsets
    readonly_fields = BaseUserAdmin.readonly_fields + ('order_count_display', 'total_spent_display', 'last_order_display')
    
    # Extend fieldsets to include user activity section with readonly fields
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Activity', {
            'fields': ('order_count_display', 'total_spent_display', 'last_order_display'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderInline, CartInline]
    
    def order_count(self, obj):
        count = Order.objects.filter(user=obj).count()
        url = reverse('admin:orders_order_changelist') + f'?user__id={obj.id}'
        return format_html('<a href="{}">{} orders</a>', url, count)
    order_count.short_description = 'Orders'
    
    def cart_status(self, obj):
        try:
            cart = Cart.objects.get(user=obj)
            item_count = cart.items.count()
            if item_count > 0:
                url = reverse('admin:cart_cart_change', args=[cart.pk])
                return format_html('<a href="{}" style="color: #ff9800;">🛒 {} item(s)</a>', url, item_count)
            return "Empty"
        except Cart.DoesNotExist:
            return "No cart"
    cart_status.short_description = 'Current Cart'
    
    def order_count_display(self, obj):
        count = Order.objects.filter(user=obj).count()
        return format_html('<strong>{}</strong>', count)
    order_count_display.short_description = 'Total Orders'
    
    def total_spent_display(self, obj):
        total = Order.objects.filter(user=obj, status__in=['delivered', 'processing', 'shipped']).aggregate(
            total=models.Sum('total_amount'))['total'] or 0
        return f"UGX {total:,.0f}"
    total_spent_display.short_description = 'Total Spent'
    
    def last_order_display(self, obj):
        last_order = Order.objects.filter(user=obj).order_by('-created_at').first()
        if last_order:
            url = reverse('admin:orders_order_change', args=[last_order.pk])
            return format_html('<a href="{}">{}</a>', url, last_order.created_at.strftime('%Y-%m-%d'))
        return "No orders"
    last_order_display.short_description = 'Last Order'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)