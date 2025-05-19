from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages

from .models import Product, Category, Brand, ProductVariant, Tag
from reviews.models import Review
from wishlist.models import Wishlist

def product_list(request):
    products = Product.objects.filter(is_active=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    tag_slug = request.GET.get('tag')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    query = request.GET.get('q')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Include products from this category and all its subcategories
        all_categories = [category]
        all_categories.extend(list(category.children.all()))
        products = products.filter(category__in=all_categories)
    
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags=tag)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popularity':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    # Default sorting is already set in model Meta class
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all active categories and brands for filters
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'current_sorting': sort_by,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.filter(is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'variants': variants,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'in_wishlist': in_wishlist,
    }
    
    return render(request, 'products/product_detail.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Include products from this category and all its subcategories
    all_categories = [category]
    all_categories.extend(list(category.children.all()))
    
    products = Product.objects.filter(category__in=all_categories, is_active=True)
    
    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    # Default sorting is already set in model Meta class
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'current_sorting': sort_by,
        'subcategories': category.children.filter(is_active=True),
    }
    
    return render(request, 'products/category_detail.html', context)


def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(tags__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    
    return render(request, 'products/search_results.html', context)


def get_variant_details(request):
    """AJAX endpoint to get selected variant details"""
    variant_id = request.GET.get('variant_id')
    try:
        variant = ProductVariant.objects.get(id=variant_id)
        return JsonResponse({
            'price': float(variant.price),
            'sale_price': float(variant.sale_price) if variant.sale_price else None,
            'stock_quantity': variant.stock_quantity,
            'is_in_stock': variant.is_in_stock,
            'image': variant.image.url if variant.image else None,
        })
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Variant not found'}, status=404)

def eid_collection(request):
    # Fetch and display Eid collection products
    return render(request, 'products/eid_collection.html')

def new_arrivals(request):
    # Get products marked as new
    new_products = Product.objects.filter(is_new=True)
    context = {
        'new_products': new_products
    }
    return render(request, 'products/new_arrivals.html', context)

def men(request):
    # Get products in the men's category
    men_products = Product.objects.filter(category__slug='men')
    context = {
        'products': men_products,
        'category': 'Men'
    }
    return render(request, 'products/category.html', context)

def women(request):
    # Get products in the women's category
    women_products = Product.objects.filter(category__slug='women')
    context = {
        'products': women_products,
        'category': 'Women'
    }
    return render(request, 'products/category.html', context)

def kids(request):
    # Get products in the kids' category
    kids_products = Product.objects.filter(category__slug='kids')
    context = {
        'products': kids_products,
        'category': 'Kids'
    }
    return render(request, 'products/category.html', context)

def men_category(request):
    # Get products in the men's category
    men_products = Product.objects.filter(category__slug='men')
    context = {
        'products': men_products,
        'category': 'Men'
    }
    return render(request, 'products/category.html', context)

def men_casual_shirts(request):
    products = Product.objects.filter(category__slug='men', tags__name='Casual Shirts')
    context = {
        'products': products,
        'category': 'Men Casual Shirts'
    }
    return render(request, 'products/category.html', context)

def men_formal_shirts(request):
    products = Product.objects.filter(category__slug='men', tags__name='Formal Shirts')
    context = {
        'products': products,
        'category': 'Men Formal Shirts'
    }
    return render(request, 'products/category.html', context)

def men_polo_shirts(request):
    products = Product.objects.filter(category__slug='men', tags__name='Polo Shirts')
    context = {
        'products': products,
        'category': 'Men Polo Shirts'
    }
    return render(request, 'products/category.html', context)

def men_t_shirts(request):
    products = Product.objects.filter(category__slug='men', tags__name='T-Shirts')
    context = {
        'products': products,
        'category': 'Men T-Shirts'
    }
    return render(request, 'products/category.html', context)

def men_chinos(request):
    products = Product.objects.filter(category__slug='men', tags__name='Chinos')
    context = {
        'products': products,
        'category': 'Men Chinos'
    }
    return render(request, 'products/category.html', context)

def men_formal_pants(request):
    products = Product.objects.filter(category__slug='men', tags__name='formal_pants')
    context = {
        'products': products,
        'category': 'Formal Pants'
    }
    return render(request, 'products/category.html', context)    

def men_jeans(request):
    products = Product.objects.filter(category__slug='men', tags__name='Jeans')
    context = {
        'products': products,
        'category': 'Men Jeans'
    }
    return render(request, 'products/category.html', context)

def men_shorts(request):
    products = Product.objects.filter(category__slug='men', tags__name='Shorts')
    context = {
        'products': products,
        'category': 'Men Shorts'
    }
    return render(request, 'products/category.html', context)

def men_panjabi(request):
    products = Product.objects.filter(category__slug='men', tags__name='panjabi')
    context = {
        'products': products,
        'category': 'Panjabi'
    }
    return render(request, 'products/category.html', context)

def men_kabli(request):
    products = Product.objects.filter(category__slug='men', tags__name='kabli')
    context = {
        'products': products,
        'category': 'Kabli And Matching Suits'
    }
    return render(request, 'products/category.html', context)

def men_fatua(request):
    products = Product.objects.filter(category__slug='men', tags__name='fatua')
    context = {
        'products': products,
        'category': 'Fatua'
    }
    return render(request, 'products/category.html', context)

def men_waistcoats(request):
    products = Product.objects.filter(category__slug='men', tags__name='waistcoats')
    context = {
        'products': products,
        'category': 'Waistcoats'
    }
    return render(request, 'products/category.html', context)

def men_pajamas(request):
    products = Product.objects.filter(category__slug='men', tags__name='pajamas')
    context = {
        'products': products,
        'category': 'Pajamas'
    }
    return render(request, 'products/category.html', context)

def women_category(request):
    # Get products in the men's category
    women_products = Product.objects.filter(category__slug='women')
    context = {
        'products': women_products,
        'category': 'Women'
    }
    return render(request, 'products/category.html', context)

def women_tops(request):
    products = Product.objects.filter(category__slug='women', tags__name='Tops')
    context = {
        'products': products,
        'category': 'Women Tops'
    }
    return render(request, 'products/category.html', context)

def women_dresses(request):
    products = Product.objects.filter(category__slug='women', tags__name='Dresses')
    context = {
        'products': products,
        'category': 'Women Dresses'
    }
    return render(request, 'products/category.html', context)

def women_jeans(request):
    products = Product.objects.filter(category__slug='women', tags__name='Jeans')
    context = {
        'products': products,
        'category': 'Women Jeans'
    }
    return render(request, 'products/category.html', context)

def women_skirts(request):
    products = Product.objects.filter(category__slug='women', tags__name='Skirts')
    context = {
        'products': products,
        'category': 'Women Skirts'
    }
    return render(request, 'products/category.html', context)

def women_blouses(request):
    products = Product.objects.filter(category__slug='women', tags__name='Blouses')
    context = {
        'products': products,
        'category': 'Women Blouses'
    }
    return render(request, 'products/category.html', context)

def women_jumpsuits(request):
    products = Product.objects.filter(category__slug='women', tags__name='Jumpsuits')
    context = {
        'products': products,
        'category': 'Women Jumpsuits'
    }
    return render(request, 'products/category.html', context)

def women_activewear(request):
    products = Product.objects.filter(category__slug='women', tags__name='Activewear')
    context = {
        'products': products,
        'category': 'Women Activewear'
    }
    return render(request, 'products/category.html', context)

def women_outerwear(request):
    products = Product.objects.filter(category__slug='women', tags__name='Outerwear')
    context = {
        'products': products,
        'category': 'Women Outerwear'
    }
    return render(request, 'products/category.html', context)

def women_lingerie(request):
    products = Product.objects.filter(category__slug='women', tags__name='Lingerie')
    context = {
        'products': products,
        'category': 'Women Lingerie'
    }
    return render(request, 'products/category.html', context)

def women_shoes(request):
    products = Product.objects.filter(category__slug='women', tags__name='Shoes')
    context = {
        'products': products,
        'category': 'Women Shoes'
    }
    return render(request, 'products/category.html', context)

def women_accessories(request):
    products = Product.objects.filter(category__slug='women', tags__name='Accessories')
    context = {
        'products': products,
        'category': 'Women Accessories'
    }
    return render(request, 'products/category.html', context)

def women_mystika(request):
    products = Product.objects.filter(category__slug='women', tags__name='Mystika')
    context = {
        'products': products,
        'category': 'Women Mystika'
    }
    return render(request, 'products/category.html', context)

def women_bling(request):
    products = Product.objects.filter(category__slug='women', tags__name='Bling')
    context = {
        'products': products,
        'category': 'Women Bling Collection'
    }
    return render(request, 'products/category.html', context)

def women_t_shirts(request):
    products = Product.objects.filter(category__slug='women', tags__name='T-Shirts')
    context = {
        'products': products,
        'category': 'Women T-Shirts'
    }
    return render(request, 'products/category.html', context)

def women_pants(request):
    products = Product.objects.filter(category__slug='women', tags__name='Pants')
    context = {
        'products': products,
        'category': 'Women Pants'
    }
    return render(request, 'products/category.html', context)

def women_tanks(request):
    products = Product.objects.filter(category__slug='women', tags__name='Tank Tops')
    context = {
        'products': products,
        'category': 'Women Tank Tops'
    }
    return render(request, 'products/category.html', context)

def women_ethnic_kurtis(request):
    products = Product.objects.filter(category__slug='women', tags__name='Ethnic Kurtis')
    context = {
        'products': products,
        'category': 'Women Ethnic Kurtis'
    }
    return render(request, 'products/category.html', context)

def women_ethnic_sets(request):
    products = Product.objects.filter(category__slug='women', tags__name='Ethnic Sets')
    context = {
        'products': products,
        'category': 'Women Ethnic Sets'
    }
    return render(request, 'products/category.html', context)

def women_lawn_kurtis(request):
    products = Product.objects.filter(category__slug='women', tags__name='Lawn Kurtis')
    context = {
        'products': products,
        'category': 'Women Lawn Kurtis'
    }
    return render(request, 'products/category.html', context)

def women_two_piece(request):
    products = Product.objects.filter(category__slug='women', tags__name='Two-Piece')
    context = {
        'products': products,
        'category': 'Women Two-Piece Lawns'
    }
    return render(request, 'products/category.html', context)

def women_three_piece(request):
    products = Product.objects.filter(category__slug='women', tags__name='Three-Piece')
    context = {
        'products': products,
        'category': 'Women Three-Piece Lawns'
    }
    return render(request, 'products/category.html', context)

def women_ethnic_pants(request):
    products = Product.objects.filter(category__slug='women', tags__name='Ethnic Pants')
    context = {
        'products': products,
        'category': 'Women Ethnic Pants'
    }
    return render(request, 'products/category.html', context)

def women_sarees(request):
    products = Product.objects.filter(category__slug='women', tags__name='Sarees')
    context = {
        'products': products,
        'category': 'Women Sarees'
    }
    return render(request, 'products/category.html', context)

def women_totes(request):
    products = Product.objects.filter(category__slug='women', tags__name='Totes')
    context = {
        'products': products,
        'category': 'Women Totes'
    }
    return render(request, 'products/category.html', context)

def kids_category(request):
    # Get products in the kids' category
    kids_products = Product.objects.filter(category__slug='kids')
    context = {
        'products': kids_products,
        'category': 'Kids'
    }
    return render(request, 'products/category.html', context)

def boys_panjabi(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Panjabi')
    context = {
        'products': products,
        'category': 'Boys Panjabi'
    }
    return render(request, 'products/category.html', context)

def boys_kabli(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Kabli')
    context = {
        'products': products,
        'category': 'Boys Kabli'
    }
    return render(request, 'products/category.html', context)

def boys_shirts(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Casual Shirts')
    context = {
        'products': products,
        'category': 'Boys Casual Shirts'
    }
    return render(request, 'products/category.html', context)

def boys_polos(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Polos')
    context = {
        'products': products,
        'category': 'Boys Polos'
    }
    return render(request, 'products/category.html', context)

def boys_tshirts(request):
    products = Product.objects.filter(category__slug='boys', tags__name='T-Shirts')
    context = {
        'products': products,
        'category': 'Boys T-Shirts'
    }
    return render(request, 'products/category.html', context)

def boys_bottoms(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Bottoms')
    context = {
        'products': products,
        'category': 'Boys Bottoms'
    }
    return render(request, 'products/category.html', context)

def boys_shorts(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Shorts')
    context = {
        'products': products,
        'category': 'Boys Shorts'
    }
    return render(request, 'products/category.html', context)

def boys_prince(request):
    products = Product.objects.filter(category__slug='boys', tags__name='Prince')
    context = {
        'products': products,
        'category': 'Prince'
    }
    return render(request, 'products/category.html', context)

def girls_ethnic_tops(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Ethnic Tops')
    context = {
        'products': products,
        'category': 'Girls Ethnic Tops'
    }
    return render(request, 'products/category.html', context)

def girls_lawn(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Lawn')
    context = {
        'products': products,
        'category': 'Girls Lawn'
    }
    return render(request, 'products/category.html', context)

def girls_tops(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Tops')
    context = {
        'products': products,
        'category': 'Girls Tops'
    }
    return render(request, 'products/category.html', context)

def girls_bottom(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Bottom')
    context = {
        'products': products,
        'category': 'Girls Bottom'
    }
    return render(request, 'products/category.html', context)

def girls_dresses(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Dresses')
    context = {
        'products': products,
        'category': 'Girls Dresses'
    }
    return render(request, 'products/category.html', context)

def girls_princess(request):
    products = Product.objects.filter(category__slug='girls', tags__name='Princess')
    context = {
        'products': products,
        'category': 'Girls Princess'
    }
    return render(request, 'products/category.html', context)

def junior_boys_panjabi(request):
    products = Product.objects.filter(category__slug='junior_boys', tags__name='Panjabi')
    context = {
        'products': products,
        'category': 'Junior Boys Panjabi'
    }
    return render(request, 'products/category.html', context)

def junior_boys_kabli(request):
    products = Product.objects.filter(category__slug='junior_boys', tags__name='Kabli')
    context = {
        'products': products,
        'category': 'Junior Boys Kabli'
    }
    return render(request, 'products/category.html', context)

def junior_boys_top(request):
    products = Product.objects.filter(category__slug='junior_boys', tags__name='Top')
    context = {
        'products': products,
        'category': 'Junior Boys Top'
    }
    return render(request, 'products/category.html', context)

def junior_boys_bottom(request):
    products = Product.objects.filter(category__slug='junior_boys', tags__name='Bottom')
    context = {
        'products': products,
        'category': 'Junior Boys Bottom'
    }
    return render(request, 'products/category.html', context)

def junior_girls_ethnic(request):
    products = Product.objects.filter(category__slug='junior_girls', tags__name='Ethnic')
    context = {
        'products': products,
        'category': 'Junior Girls Ethnic'
    }
    return render(request, 'products/category.html', context)

def junior_girls_lawn(request):
    products = Product.objects.filter(category__slug='junior_girls', tags__name='Lawn')
    context = {
        'products': products,
        'category': 'Junior Girls Lawn'
    }
    return render(request, 'products/category.html', context)

def junior_girls_top(request):
    products = Product.objects.filter(category__slug='junior_girls', tags__name='Top')
    context = {
        'products': products,
        'category': 'Junior Girls Top'
    }
    return render(request, 'products/category.html', context)

def junior_girls_bottom(request):
    products = Product.objects.filter(category__slug='junior_girls', tags__name='Bottom')
    context = {
        'products': products,
        'category': 'Junior Girls Bottom'
    }
    return render(request, 'products/category.html', context)

def shop_view(request):
    # Your shop view logic
    return render(request, 'products/shop.html')