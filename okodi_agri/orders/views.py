# okodi_agri/orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cart.models import Cart, CartItem
from .models import Order, OrderItem

def order_create(request):
    """Create a new order from cart"""
    # Get cart
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        if request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
        else:
            cart = None
    
    if not cart or cart.items.count() == 0:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        # Process the order
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        district = request.POST.get('district')
        payment_method = request.POST.get('payment_method')
        delivery_notes = request.POST.get('delivery_notes', '')
        
        # Validate required fields
        if not all([full_name, email, phone, address, city, district, payment_method]):
            messages.error(request, 'Please fill in all required fields')
            context = {
                'cart': cart,
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'address': address,
                'city': city,
                'district': district,
                'payment_method': payment_method,
                'delivery_notes': delivery_notes,
            }
            return render(request, 'orders/order_create.html', context)
        
        # Calculate totals
        subtotal = cart.get_total_price()
        delivery_fee = 5000
        total_amount = subtotal + delivery_fee
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            cart=cart,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            district=district,
            payment_method=payment_method,
            delivery_notes=delivery_notes,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            status='pending'
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Update product stock
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            if product.stock_quantity == 0:
                product.is_available = False
            product.save()
        
        # Clear the cart
        cart.items.all().delete()
        
        # Success message
        messages.success(request, f'Order #{order.order_number} created successfully!')
        
        # Redirect to order detail
        return redirect('orders:order_detail', order_id=order.id)
    
    # GET request - show order form
    context = {
        'cart': cart,
        'delivery_fee': 5000,
        'subtotal': cart.get_total_price(),
        'total': cart.get_total_price() + 5000,
    }
    return render(request, 'orders/order_create.html', context)

@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user owns this order or is admin
    if order.user != request.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this order')
        return redirect('shop:product_list')
    
    context = {
        'order': order,
        'order_items': order.items.all().select_related('product'),
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_list(request):
    """List all orders for the logged-in user"""
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)

# Demo: Mock payment processing (for demo purposes)
def process_payment(request, order_id):
    """Mock payment processing - for demo only"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        # Mock payment success
        if order.payment_method == 'cash':
            order.status = 'processing'
            order.save()
            messages.info(request, 'Order placed! You will pay cash upon delivery.')
        else:
            # Simulate mobile money/bank payment
            messages.info(request, f'Payment via {order.get_payment_method_display()} will be processed. Demo mode - order confirmed!')
            order.status = 'processing'
            order.save()
        
        return redirect('orders:order_detail', order_id=order.id)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
