# okodi_agri/orders/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total_price']
    fields = ['product', 'quantity', 'price', 'total_price']
    
    def total_price(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_price.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_link', 'full_name', 'status', 'payment_method', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'subtotal', 'total_amount']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('user_link_display', 'full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'district', 'zip_code', 'delivery_notes')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'delivery_fee', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Guest"
    user_link.short_description = 'User'
    
    def user_link_display(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('User: <a href="{}"><strong>{}</strong></a>', url, obj.user.username)
        return "Guest user"
    user_link_display.short_description = 'User Account'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = 'Mark as Processing'
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark as Shipped'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark as Delivered'
    
    def mark_as_cancelled(self, request, queryset):
        for order in queryset:
            # Restore stock when order is cancelled
            for item in order.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                if product.stock_quantity > 0:
                    product.is_available = True
                product.save()
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders cancelled and stock restored.')
    mark_as_cancelled.short_description = 'Cancel Orders'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'product_link', 'quantity', 'price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']
    readonly_fields = ['total_price']
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Order'
    
    def product_link(self, obj):
        url = reverse('admin:shop_product_change', args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def total_price(self, obj):
        return f"UGX {obj.get_total_price():,.0f}"
    total_price.short_description = 'Total'