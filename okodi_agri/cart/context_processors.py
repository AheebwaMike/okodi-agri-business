# okodi_agri/cart/context_processors.py

from .models import Cart, CartItem

def cart_count(request):
    """Add cart count to all templates"""
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.get_total_items()
        except Cart.DoesNotExist:
            cart_count = 0
    elif request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            cart_count = cart.get_total_items()
        except Cart.DoesNotExist:
            cart_count = 0
    
    return {'cart_count': cart_count}