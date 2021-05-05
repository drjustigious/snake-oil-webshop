import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from snakeoil_webshop import helpers
from snakeoil_webshop.forms import ProductSearchForm, AddToCartForm
from snakeoil_webshop.models import Product, ShoppingCart, ShoppingCartItem

# Import the whole serializers module to extend Product with the as_json method.
import snakeoil_webshop.serializers


# Constants for identifying which view is getting rendered.
SHOP = "SHOP"
PRODUCT_MANAGEMENT = "PRODUCT_MANAGEMENT"
SHOPPING_CART = "SHOPPING_CART"


class ShopView(LoginRequiredMixin, TemplateView):
    
    template_name = "shop.html"

    login_url = '/login/'
    redirect_field_name = 'next'


    def get_context_data(self, *args, **kwargs):
        context = super(ShopView, self).get_context_data(*args, **kwargs)

        if self.request.method == 'POST':
            # We received a filled product search form from the user.
            form = ProductSearchForm(self.request.POST)
            products = form.filter_results()
        else:
            # We're serving the shop page out for the first time with an empty search form.
            form = ProductSearchForm()
            products = form.give_all_results()

        active_shopping_cart = helpers.find_active_cart_for_user(self.request.user)

        added_context = {
            "form": form,
            "products": products,
            "active_view": SHOP,
            "shopping_cart_string": active_shopping_cart.summarize()
        }
        context.update(added_context)

        return context


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class AddToCartView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # The validation checks that we have an integer for the product pk
        # and if there is something for the number of items to add, that
        # that too is an integer.
        validation_form = AddToCartForm(request.data)
        if not validation_form.is_valid():
            return Response(
                "Bad request. Form invalid.",
                status=400
            )

        product_id = validation_form.cleaned_data.get("pk")
        num_items_to_add = validation_form.cleaned_data.get("num_items", None)
        # Add one item unless told otherwise.
        if num_items_to_add is None:
            num_items_to_add = 1

        # Looks like we have an integer for the product identifier.
        # Does it correspond to an existing Product?
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                f"The indicated product (ID: {product_id}) does not exist.",
                status=404
            )

        # We have a product, let's put it into the acting user's cart.
        shopping_cart, cart_created = ShoppingCart.objects.get_or_create(
            user=request.user
        )
        cart_item, item_created = ShoppingCartItem.objects.get_or_create(
            shopping_cart=shopping_cart,
            product=product
        )

        # Update the number of carted items corresponding to the added product.
        if item_created:
            cart_item.num_items = num_items_to_add
        else:
            cart_item.num_items += num_items_to_add
        cart_item.save()

        response_data = {
            "product": product.as_json(),
            "num_items_added": num_items_to_add,
            "cart_summary": shopping_cart.summarize()
        }

        return Response(response_data, status=200)