from django.contrib import admin
from snakeoil_webshop.models import Product, ShoppingCart, ShoppingCartItem


class ProductAdmin(admin.ModelAdmin):
    fields = [
        'sku',
        'description',
        'created',
        'updated',
        'price',
        'num_in_stock'
    ]
    
    readonly_fields = ['created', 'updated']


class ShoppingCartItemInline(admin.StackedInline):
    model = ShoppingCartItem
    extra = 3


class ShoppingCartAdmin(admin.ModelAdmin):
    fields = ['user']
    inlines = [ShoppingCartItemInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)