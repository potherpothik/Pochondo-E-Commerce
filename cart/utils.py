from .models import Cart

def get_or_create_cart(request):
    """
    Get the cart for the current user or session, or create a new one if it doesn't exist
    """
    if request.user.is_authenticated:
        # Get or create a cart for the logged-in user
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # If there was an anonymous cart, transfer its items to the user's cart
        if 'cart_id' in request.session:
            anonymous_cart_id = request.session['cart_id']
            try:
                anonymous_cart = Cart.objects.get(id=anonymous_cart_id, user__isnull=True)
                
                # Transfer items from anonymous cart to user cart
                for item in anonymous_cart.items.all():
                    # Check if the same product and variant are already in the user's cart
                    try:
                        existing_item = cart.items.get(product=item.product, variant=item.variant)
                        # Update quantity
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    except cart.items.model.DoesNotExist:
                        # Move item to user's cart
                        item.cart = cart
                        item.save()
                
                # Delete the anonymous cart and remove from session
                anonymous_cart.delete()
                del request.session['cart_id']
            except Cart.DoesNotExist:
                # Invalid cart in session, just remove it
                if 'cart_id' in request.session:
                    del request.session['cart_id']
    else:
        # Get or create a cart for the anonymous user
        if 'cart_id' in request.session:
            try:
                cart = Cart.objects.get(id=request.session['cart_id'], user__isnull=True)
            except Cart.DoesNotExist:
                # Create a new cart if the one in session doesn't exist
                cart = Cart.objects.create(session_id=request.session.session_key)
                request.session['cart_id'] = cart.id
        else:
            # Ensure we have a session key
            if not request.session.session_key:
                request.session.save()
            
            # Create a new cart
            cart = Cart.objects.create(session_id=request.session.session_key)
            request.session['cart_id'] = cart.id
    
    return cart
