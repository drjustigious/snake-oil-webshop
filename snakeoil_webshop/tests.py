from snakeoil_webshop.models import Product
from snakeoil_webshop import helpers
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from snakeoil_webshop.management.commands import add_demo_users, add_demo_products


class PermissionsTestCase(TestCase):
    """
    Verify that each user group can see the appropriate resources,
    and only those resources.
    """

    def setUp(self):
        add_demo_users.Command().handle(silent=True)

        self.staff_user = User.objects.get(username=add_demo_users.Command.STAFF_USERNAME)
        self.manager = User.objects.get(username=add_demo_users.Command.MANAGER_USERNAME)
        self.customer = User.objects.get(username=add_demo_users.Command.CUSTOMER_X_USERNAME)

        self.client = Client()


    def test_everyone_can_see_shop(self):
        """
        Everyone can see the main shop page.
        """
        self.assert_get_url_status_as_user(
            self.customer,
            "shop",
            200
        )
        self.assert_get_url_status_as_user(
            self.manager,
            "shop",
            200
        )
        self.assert_get_url_status_as_user(
            self.staff_user,
            "shop",
            200
        )


    def test_everyone_can_see_shopping_cart(self):
        """
        Everyone can see the shopping cart.
        """
        self.assert_get_url_status_as_user(
            self.customer,
            "shopping-cart",
            200
        )
        self.assert_get_url_status_as_user(
            self.manager,
            "shopping-cart",
            200
        )
        self.assert_get_url_status_as_user(
            self.staff_user,
            "shopping-cart",
            200
        )


    def test_customer_cannot_see_product_management(self):
        """
        Ordinary customers should not be able to access
        the product management page. They will be redirected
        to login instead.
        """
        self.assert_get_redirected_to_login(
            self.customer,
            "product-management"
        )
        self.assert_get_url_status_as_user(
            self.manager,
            "product-management",
            200
        )
        self.assert_get_url_status_as_user(
            self.staff_user,
            "product-management",
            200
        )


    def assert_get_url_status_as_user(self, user, url_name, expected_http_status):
        """
        Log in as the given user, try to GET the given URL
        and assert that the response status was as expected.
        """
        self.client.force_login(user)
        response = self.client.get(
            reverse(url_name)
        )
        self.assertEqual(response.status_code, expected_http_status)
        self.client.logout()


    def assert_get_redirected_to_login(self, user, url_name):
        self.client.force_login(user)
        response = self.client.get(
            reverse(url_name)
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.get("Location").startswith("login"))
        self.client.logout()


class CartTransactionsTestCase(TestCase):
    """
    Verify that a customer can add and remove products
    to and from their shopping cart.
    """

    def setUp(self):
        add_demo_users.Command().handle(silent=True)
        add_demo_products.Command().handle(silent=True)

        self.customer = User.objects.get(username=add_demo_users.Command.CUSTOMER_X_USERNAME)
        self.client = Client()


    def test_can_add_single_items_to_cart(self):
        """
        Add two individual items to the shopping cart
        with an implied item count of 1 each.
        """
        products_to_add = [
            Product.objects.get(sku=add_demo_products.Command.SKU001),
            Product.objects.get(sku=add_demo_products.Command.SKU002)
        ]

        self.client.force_login(self.customer)

        # Add first item.
        response = self.client.post(
            reverse("add-to-cart"),
            {'pk': products_to_add[0].pk}
        )
        self.assertEqual(response.status_code, 200)

        # Add second item.
        response = self.client.post(
            reverse("add-to-cart"),
            {'pk': products_to_add[1].pk}
        )
        self.assertEqual(response.status_code, 200)

        # Check what's in the cart.
        cart = helpers.find_active_cart_for_user(self.customer)
        products_in_cart = [
            cart.shopping_cart_items.select_related("product").get(product=products_to_add[0]),
            cart.shopping_cart_items.select_related("product").get(product=products_to_add[1])
        ]

        self.assertEqual(products_to_add[0].pk, products_in_cart[0].product.pk)
        self.assertEqual(products_to_add[1].pk, products_in_cart[1].product.pk)

        self.client.logout()


    def test_can_add_multiple_items_of_product_to_cart(self):
        """
        Verify that it's possible how many items of a given product
        should be dropped into the shopping cart.
        """
        product_to_add = Product.objects.get(sku=add_demo_products.Command.SKU001)
        num_to_add = 3

        self.client.force_login(self.customer)

        # Add the items twice.
        response = self.client.post(
            reverse("add-to-cart"),
            {
                'pk': product_to_add.pk,
                'num_items': num_to_add
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("add-to-cart"),
            {
                'pk': product_to_add.pk,
                'num_items': num_to_add
            }
        )
        self.assertEqual(response.status_code, 200)        

        # Check what's in the cart.
        cart = helpers.find_active_cart_for_user(self.customer)
        cart_item = cart.shopping_cart_items.select_related("product").get(product=product_to_add)
        self.assertEqual(cart_item.num_items, 2*num_to_add)

        self.client.logout()