# okodi_agri/cart/views.py

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from shop.models import Product
from .models import Cart, CartItem

def get_or_create_cart(request):
    """Get or create cart for current user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If there was a session cart, merge it
        if request.session.session_key and not created:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    # Ensure session is saved
    request.session.modified = True
    
    return cart


def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.all().select_related('product'),
    }
    return render(request, 'cart/cart_detail.html', context)

@require_POST
def cart_add(request, product_id):
    """Add product to cart (AJAX endpoint)"""
    try:
        product = get_object_or_404(Product, id=product_id, is_available=True)
        cart = get_or_create_cart(request)
        
        # Parse JSON data
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        
        # Check stock availability
        if quantity > product.stock_quantity:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock_quantity} items available in stock'
            }, status=400)
        
        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot add {quantity} more. Only {product.stock_quantity - cart_item.quantity} left'
                }, status=400)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Get updated cart count
        cart_count = cart.get_total_items()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': f'{product.name} added to cart',
            'item_quantity': cart_item.quantity,
            'item_total': float(cart_item.get_total_price())
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def cart_update(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        try:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            if quantity <= 0:
                cart_item.delete()
            else:
                if quantity > cart_item.product.stock_quantity:
                    return JsonResponse({
                        'success': False,
                        'error': f'Only {cart_item.product.stock_quantity} items available'
                    }, status=400)
                cart_item.quantity = quantity
                cart_item.save()
            
            cart = get_or_create_cart(request)  # Refresh cart
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_total_items(),
                'cart_total': float(cart.get_total_price()),
                'item_total': float(cart_item.get_total_price()) if quantity > 0 else 0
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def cart_remove(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            
            cart = get_or_create_cart(request)  # Refresh cart
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_total_items(),
                'cart_total': float(cart.get_total_price())
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)