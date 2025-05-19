from django.db.models import F
from django.core.mail import send_mail
from products.models import Product, ProductVariant

def send_low_stock_alert():
    # gather low‐stock products and variants
    low_products = Product.objects.filter(is_active=True, stock_quantity__lte=F('low_stock_threshold'))
    low_variants = ProductVariant.objects.filter(is_active=True, stock_quantity__lte=F('product__low_stock_threshold'))

    # if nothing found, bail out early
    if not low_products.exists() and not low_variants.exists():
        return  # no products in development, so safe to exit

    # otherwise build alert
    subject = "Low Stock Alert"
    lines = []
    for p in low_products:
        lines.append(f"Product: {p.name} (SKU {p.sku}) has only {p.stock_quantity} items left.")
    for v in low_variants:
        lines.append(f"Variant: {v.full_sku} has only {v.stock_quantity} items left.")
    message = "\n".join(lines)

    send_mail(
        subject,
        message,
        "alerts@yourdomain.com",
        ["admin@yourdomain.com"],
        fail_silently=False,
    )
