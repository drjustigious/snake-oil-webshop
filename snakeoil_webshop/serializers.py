import json

from django.db.models import Sum, F
from rest_framework.serializers import ModelSerializer
from snakeoil_webshop.models import Product, ShoppingCart


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'pk',
            'sku',
            'name',
            'description',
            'created',
            'updated',
            'price',
            'num_in_stock'
        ]


# Extend the Product model with an 'as_json' convenience method.
def product_as_json(self):
    """
    Return a JSON repesentation of the Product.
    """
    serializer = ProductSerializer(self)
    json_string = json.dumps(serializer.data, ensure_ascii=False)

    return json_string

setattr(Product, 'as_json', product_as_json)


# Extend the ShoppingCart model with a summary serializer method.
def cart_summary_as_string(self):
    """
    Return a short string representing the contents
    of the shopping cart.
    """
    total_num_items = self.shopping_cart_items.aggregate(
            total_num_items=Sum('num_items'),
        ).get('total_num_items', 0)

    total_price = self.shopping_cart_items.aggregate(
            total_price=Sum(
                F('product__price')*F('num_items')
            )
        ).get('total_price', 0.00)

    summary_string = f"{total_num_items} items | {total_price} €"
    return summary_string

setattr(ShoppingCart, 'summarize', cart_summary_as_string)