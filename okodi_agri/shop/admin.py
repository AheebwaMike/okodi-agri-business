# okodi_agri/shop/admin.py

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name', 'category__name', 'price', 'stock_quantity', 
                  'description', 'product_type', 'supplier_name')
        export_order = ('name', 'category__name', 'price', 'stock_quantity', 'product_type')



class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        count = obj.products.count()
        url = reverse('admin:shop_product_changelist') + f'?category__id={obj.id}'
        return format_html('<a href="{}">{} products</a>', url, count)
    product_count.short_description = 'Products'

class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_available', 'product_type', 'created_at']
    list_filter = ['category', 'is_available', 'product_type', 'created_at']
    search_fields = ['name', 'description', 'supplier_name', 'sku']
    list_editable = ['price', 'stock_quantity', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'display_image']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'product_type')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Product Specifications', {
            'fields': ('weight', 'measurement')
        }),
        ('Supplier Information', {
            'fields': ('supplier_name', 'supplier_location'),
            'classes': ('collapse',)
        }),
        ('Product Images', {
            'fields': ('main_image', 'additional_image_1', 'additional_image_2', 'additional_image_3', 'display_image'),
            'description': 'Upload high-quality images for better product visibility'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_image(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 8px;" />', obj.main_image.url)
        return "No image"
    display_image.short_description = 'Current Image'
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)
    
    actions = ['make_available', 'make_unavailable', 'increase_stock']
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} products marked as available.')
    make_available.short_description = 'Mark selected products as available'
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    make_unavailable.short_description = 'Mark selected products as unavailable'
    
    def increase_stock(self, request, queryset):
        for product in queryset:
            product.stock_quantity += 100
            product.save()
        self.message_user(request, f'Added 100 units to {queryset.count()} products.')
    increase_stock.short_description = 'Add 100 units to stock'

# Register the admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

# Customize admin site header
admin.site.site_header = 'Okodi Agri-Business Admin'
admin.site.site_title = 'Okodi Agri CMS'
admin.site.index_title = 'Product Management Dashboard'