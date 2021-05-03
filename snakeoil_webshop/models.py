from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    """
    An abstract product definition. To keep things simple, we also include
    price and stock count information right in this model.
    """

    # Text fields for identifying the product.
    sku = models.SlugField(unique=True)
    description = models.TextField()

    # Timestamps for monitoring the life cycle of the product.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # These fields should really be derived from other models,
    # but let's just keep things simple and include some per-product
    # constants here.
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=8)
    num_in_stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sku} - {self.description}"

    
class ShoppingCart(models.Model):
    """
    A collection of shopped items associated with a particular user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Cart {self.pk} of {self.user.username}"    


class ShoppingCartItem(models.Model):
    """
    A single entry in the shopping cart. Represents a given number of
    physical items corresponding to a given product definition.
    """
    class Meta:
        # Make sure we don't get two entries of the same product in
        # any shopping cart.
        unique_together = ['shopping_cart', 'product']

    shopping_cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name="shopping_cart_items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="shopping_cart_items"
    )

    num_items = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.num_items} x {self.product.sku}"