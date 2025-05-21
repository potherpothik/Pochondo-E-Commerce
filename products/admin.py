from django.contrib import admin
from .models import Category,Brand, Product, ProductAttribute, ProductAttributeValue, ProductImage, ProductVariant,  Tag
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductImage)
admin.site.register(Tag)
admin.site.register(ProductVariant)
admin.site.register(Brand)