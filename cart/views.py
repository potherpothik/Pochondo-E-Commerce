from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem, Coupon
from products.models import Product, ProductVariant
from .utils import get_or_create_cart

def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id', None)
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Validate variant if provided
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)
        # Check if variant is in stock
        if not variant.is_in_stock:
            messages.error(request, "Sorry, this variant is out of stock.")
            return redirect('products:product_detail', slug=product.slug)
        
        # Check requested quantity against stock
        if variant.stock_quantity < quantity:
            messages.error(request, f"Sorry, only {variant.stock_quantity} items in stock.")
            return redirect('products:product_detail', slug=product.slug)
    else:
        # Check if base product is in stock
        if not product.is_in_stock:
            messages.error(request, "Sorry, this product is out of stock.")
            return redirect('products:product_detail', slug=product.slug)
        
        # Check requested quantity against stock
        if product.stock_quantity < quantity:
            messages.error(request, f"Sorry, only {product.stock_quantity} items in stock.")
            return redirect('products:product_detail', slug=product.slug)
    
    # Get or create cart
    cart = get_or_create_cart(request)
    
    # Try to get existing cart item
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, variant=variant)
        # Update quantity
        cart_item.quantity = cart_item.quantity + quantity
        cart_item.save()
        messages.success(request, f"{product.name} quantity updated in your cart.")
    except CartItem.DoesNotExist:
        # Create new cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity
        )
        messages.success(request, f"{product.name} added to your cart.")
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"{product.name} added to your cart.",
            'cart_total_items': cart.item_count
        })
    
    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Ensure the cart belongs to the current session or user
    cart = get_or_create_cart(request)
    if cart_item.cart.id != cart.id:
        messages.error(request, "You don't have permission to modify this cart.")
        return redirect('cart:cart_detail')
    
    # Remove the item
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Item removed from cart.",
            'cart_total_items': cart.item_count,
            'cart_total': float(cart.total)
        })
    
    return redirect('cart:cart_detail')


@require_POST
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Ensure the cart belongs to the current session or user
    cart = get_or_create_cart(request)
    if cart_item.cart.id != cart.id:
        messages.error(request, "You don't have permission to modify this cart.")
        return redirect('cart:cart_detail')
    
    # Check if requested quantity is in stock
    if cart_item.variant:
        if cart_item.variant.stock_quantity < quantity:
            messages.error(request, f"Sorry, only {cart_item.variant.stock_quantity} items in stock.")
            quantity = cart_item.variant.stock_quantity
    else:
        if cart_item.product.stock_quantity < quantity:
            messages.error(request, f"Sorry, only {cart_item.product.stock_quantity} items in stock.")
            quantity = cart_item.product.stock_quantity
    
    # Update the quantity
    cart_item.quantity = quantity
    cart_item.save()
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total),
            'cart_total': float(cart.total),
            'cart_total_items': cart.item_count
        })
    
    return redirect('cart:cart_detail')


@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code')
    cart = get_or_create_cart(request)
    
    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        
        # Check if coupon is valid
        if coupon.is_valid(user=request.user, cart_total=cart.total):
            # Apply coupon to cart
            cart.coupon = coupon
            cart.save()
            messages.success(request, "Coupon applied successfully.")
        else:
            messages.error(request, "This coupon is invalid or has expired.")
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
    
    return redirect('cart:cart_detail')


@require_POST
def remove_coupon(request):
    cart = get_or_create_cart(request)
    
    if cart.coupon:
        cart.coupon = None
        cart.save()
        messages.success(request, "Coupon removed.")
    
    return redirect('cart:cart_detail')


def clear_cart(request):
    cart = get_or_create_cart(request)
    
    # Delete all items in the cart
    cart.items.all().delete()
    messages.success(request, "Your cart has been cleared.")
    
    return redirect('cart:cart_detail')
