# okodi_agri/shop/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from .models import Product, Category

def product_list(request, category_slug=None):
    """Display all products with advanced filtering and sorting"""
    products = Product.objects.filter(is_available=True, stock_quantity__gt=0)
    category = None
    categories = Category.objects.annotate(product_count=Count('products'))
    
    # Category filtering
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(supplier_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Product type filtering
    product_type = request.GET.get('type')
    if product_type and product_type != 'all':
        products = products.filter(product_type=product_type)
    
    # Price range filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
        'oldest': 'created_at',
        'popular': '-stock_quantity'  # Assuming more stock = more popular
    }
    if sort_by in sort_options:
        products = products.order_by(sort_options[sort_by])
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'search_query': search_query,
        'current_type': product_type,
        'current_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id, slug):
    """Display detailed view of a single product"""
    product = get_object_or_404(Product, id=product_id, slug=slug, is_available=True)
    
    # Get related products from the same category
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)