import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView
from django.db.models import Sum, F

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from snakeoil_webshop import helpers
from snakeoil_webshop.forms import ProductSearchForm, AddToCartForm, ProductCreationForm
from snakeoil_webshop.models import Product, ShoppingCart, ShoppingCartItem

# Import the whole serializers module to extend Product with the as_json method.
import snakeoil_webshop.serializers  # type: ignore


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
            "num_results": len(products),
            "active_view": SHOP,
            "shopping_cart_string": active_shopping_cart.summarize()
        }
        context.update(added_context)

        return context


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)



class ProductManagementView(ShopView):

    template_name = "product_management.html"

    login_url = '/login/'
    redirect_field_name = 'next'


    def get_context_data(self, *args, **kwargs):
        context = super(ShopView, self).get_context_data(*args, **kwargs)
        new_product = None

        if self.request.method == 'POST':
            # We received a filled product creation form from the user.
            # Remember the settings to make it easier to add similar products.
            form = ProductCreationForm(self.request.POST)
            if form.is_valid():
                new_product = self.create_new_product(form.cleaned_data)
        else:
            # We're serving the product management page out for the first time
            # with an empty product creation form.
            form = ProductCreationForm()

        products = form.give_all_results()
        active_shopping_cart = helpers.find_active_cart_for_user(self.request.user)

        added_context = {
            "form": form,
            "products": products,
            "num_results": len(products),
            "new_product": new_product,
            "active_view": PRODUCT_MANAGEMENT,
            "shopping_cart_string": active_shopping_cart.summarize()
        }
        context.update(added_context)

        return context


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


    def create_new_product(self, cleaned_data):
        """
        Create a new product corresponding to the given
        cleaned data from a ProductCreationForm.
        """
        product = Product.objects.create(**cleaned_data)
        return product


class ShoppingCartView(LoginRequiredMixin, TemplateView):

    template_name = "shopping_cart.html"

    login_url = '/login/'
    redirect_field_name = 'next'


    def get_context_data(self, *args, **kwargs):
        context = super(ShoppingCartView, self).get_context_data(*args, **kwargs)

        active_shopping_cart = helpers.find_active_cart_for_user(self.request.user)
        items_in_cart = active_shopping_cart.shopping_cart_items.select_related("product")

        total_num_items = active_shopping_cart.shopping_cart_items.aggregate(
                total_num_items=Sum('num_items'),
            ).get('total_num_items', 0)

        total_price = active_shopping_cart.shopping_cart_items.aggregate(
                total_price=Sum(
                    F('product__price')*F('num_items')
                )
            ).get('total_price', 0.00)        

        additional_context = {
            "items_in_cart": items_in_cart,
            "num_items": total_num_items,
            "total_price": total_price,
            "active_view": SHOPPING_CART,
            "shopping_cart_string": active_shopping_cart.summarize()
        }
        context.update(additional_context)

        return context



class AddToCartView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # The validation checks that we have an integer for the product pk
        # and if there is something for the number of items to add, that
        # that too is an integer.
        validation_form = AddToCartForm(request.data)
        if not validation_form.is_valid():
            return Response(
                "Bad request.",
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



class ClearCartView(RedirectView):
    """
    A view that clears the requesting user's shopping cart
    and redirects them back to see the empty cart.
    """
    permanent = False
    query_string = True
    pattern_name = "shopping-cart"


    def get_redirect_url(self, *args, **kwargs):
        """
        Clear the requesting user's cart before redirecting.
        """
        active_shopping_cart = helpers.find_active_cart_for_user(self.request.user)
        active_shopping_cart.shopping_cart_items.all().delete()

        return super().get_redirect_url(*args, **kwargs)