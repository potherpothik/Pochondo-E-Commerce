from .utils import get_or_create_cart

def cart(request):
    """
    Context processor to make cart available on all templates
    """
    if request.user.is_authenticated or 'cart_id' in request.session:
        cart = get_or_create_cart(request)
        return {'cart': cart}
    return {'cart': None}
