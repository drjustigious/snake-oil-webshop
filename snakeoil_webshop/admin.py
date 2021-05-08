from django.contrib import admin
from django.db.models import Sum, F
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
    list_display = ['__str__', 'created', 'updated', 'price', 'num_in_stock']


class ShoppingCartItemInline(admin.StackedInline):
    model = ShoppingCartItem
    extra = 3


class ShoppingCartAdmin(admin.ModelAdmin):    

    fields = ['user', 'item_count', 'total_price']
    readonly_fields = ['item_count', 'total_price']
    list_display = ['__str__', 'item_count', 'total_price']
    inlines = [ShoppingCartItemInline]

    def item_count(self, obj):
        total_num_items = obj.shopping_cart_items.aggregate(
            total_num_items=Sum('num_items')
        ).get('total_num_items', 0)
        
        return total_num_items

    def total_price(self, obj):
        total_price = obj.shopping_cart_items.aggregate(
            total_price=Sum(
                F('product__price')*F('num_items')
            )
        ).get('total_price', 0.00)

        return total_price        


admin.site.register(Product, ProductAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)