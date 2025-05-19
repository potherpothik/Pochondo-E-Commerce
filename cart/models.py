from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant
from django.utils.functional import cached_property
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import TimeStampedModel

class Cart(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store session key for anonymous users
    session_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Coupon code applied to cart
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return f"Anonymous Cart {self.session_id}"
    
    @cached_property
    def total(self):
        """
        Calculate the total price of all items in the cart
        """
        return sum(item.total for item in self.items.all())
    
    @cached_property
    def subtotal(self):
        """
        Calculate the subtotal (without discounts)
        """
        return sum(item.subtotal for item in self.items.all())
    
    @cached_property
    def discount_amount(self):
        """
        Calculate the total discount amount
        """
        discount = 0
        if self.coupon and self.coupon.is_valid():
            if self.coupon.discount_type == 'percentage':
                discount = self.subtotal * (self.coupon.discount_value / 100)
            else:  # fixed amount
                discount = min(self.coupon.discount_value, self.subtotal)  # Ensure discount doesn't exceed subtotal
        return discount
    
    @cached_property
    def final_total(self):
        """
        Return the final total after applying discounts
        """
        return self.total - self.discount_amount
    
    @cached_property
    def item_count(self):
        """
        Return the total number of items in the cart
        """
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('cart', 'product', 'variant')
    
    def __str__(self):
        if self.variant:
            return f"{self.quantity} of {self.product.name} - {self.variant}"
        return f"{self.quantity} of {self.product.name}"
    
    @property
    def unit_price(self):
        """
        Return the unit price (considering variant, if any)
        """
        if self.variant:
            return self.variant.price
        return self.product.price
    
    @property
    def unit_sale_price(self):
        """
        Return the unit sale price (considering variant, if any)
        """
        if self.variant:
            return self.variant.sale_price
        return self.product.sale_price
    
    @property
    def effective_price(self):
        """
        Return the effective price (sale price if available, otherwise regular price)
        """
        sale_price = self.unit_sale_price
        if sale_price is not None:
            return sale_price
        return self.unit_price
    
    @property
    def subtotal(self):
        """
        Return the subtotal (unit price * quantity)
        """
        return self.unit_price * self.quantity
    
    @property
    def total(self):
        """
        Return the total (effective price * quantity)
        """
        return self.effective_price * self.quantity
    
    @property
    def saved_amount(self):
        """
        Return how much is saved with the sale price
        """
        if self.unit_sale_price is not None:
            return (self.unit_price - self.unit_sale_price) * self.quantity
        return 0


class Coupon(TimeStampedModel):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # Percentage or fixed amount
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)  # How many times the coupon can be used in total
    max_uses_per_user = models.PositiveIntegerField(default=1)  # How many times the coupon can be used by one user
    is_active = models.BooleanField(default=True)
    
    # Relations
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='applicable_coupons')
    applicable_categories = models.ManyToManyField('products.Category', blank=True, related_name='applicable_coupons')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code
    
    def is_valid(self, user=None, cart_total=None):
        """
        Check if coupon is valid in the current context
        """
        from django.utils import timezone
        now = timezone.now()
        
        # General validity checks
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        
        # Check usage limits
        if self.max_uses > 0:
            used_count = CouponUsage.objects.filter(coupon=self).count()
            if used_count >= self.max_uses:
                return False
        
        # Check user specific limits
        if user and user.is_authenticated and self.max_uses_per_user > 0:
            user_used_count = CouponUsage.objects.filter(coupon=self, user=user).count()
            if user_used_count >= self.max_uses_per_user:
                return False
        
        # Check minimum purchase amount
        if cart_total and cart_total < self.min_purchase_amount:
            return False
        
        return True


class CouponUsage(TimeStampedModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        if self.user:
            return f"{self.coupon.code} used by {self.user.email} on {self.used_at}"
        return f"{self.coupon.code} used on {self.used_at}"
