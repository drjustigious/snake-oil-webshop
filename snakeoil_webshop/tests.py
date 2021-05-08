import decimal

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


    def test_can_clear_cart(self):
        """
        Verify that a customer can clear their shopping cart.
        """
        product_to_add = Product.objects.get(sku=add_demo_products.Command.SKU001)
        num_to_add = 3

        self.client.force_login(self.customer)

        # Add items to cart.
        response = self.client.post(
            reverse("add-to-cart"),
            {
                'pk': product_to_add.pk,
                'num_items': num_to_add
            }
        )
        self.assertEqual(response.status_code, 200)

        # Clear the cart. The user should be redirected back to the cart view.
        response = self.client.get(
            reverse("clear-cart")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get("Location"), reverse("shopping-cart"))

        # Assert the cart is empty.
        cart = helpers.find_active_cart_for_user(self.customer)
        cart_items = cart.shopping_cart_items.all() or None
        self.assertIsNone(cart_items)

        self.client.logout()


class ProductManagementTestCase(TestCase):
    """
    Verify a shop manager can add new product definitions.
    Also verify an ordinary customer can't.
    """

    def setUp(self):
        add_demo_users.Command().handle(silent=True)

        self.manager = User.objects.get(username=add_demo_users.Command.MANAGER_USERNAME)
        self.customer = User.objects.get(username=add_demo_users.Command.CUSTOMER_X_USERNAME)

        self.client = Client()


    def test_manager_can_add_new_product(self):
        """
        Verify that a shop manager can add a new product.
        """
        SKU = "sku"
        NAME = "name"
        DESCRIPTION = "description"
        PRICE = "price"
        NUM_IN_STOCK = "num_in_stock"

        test_product_details = {
            SKU: "SKU005",
            NAME: "testname",
            DESCRIPTION: "test description",
            PRICE: decimal.Decimal("9.99"),
            NUM_IN_STOCK: 123
        }

        # Create the new product.
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("product-management"),
            test_product_details
        )
        # TODO: The standard HTTP status for "created" would be 201.
        self.assertEqual(response.status_code, 200)

        # Find the new product and check that the details match.
        product = Product.objects.get(sku=test_product_details[SKU])

        self.assertEqual(product.sku, test_product_details[SKU])
        self.assertEqual(product.name, test_product_details[NAME])
        self.assertEqual(product.description, test_product_details[DESCRIPTION])
        self.assertEqual(product.price, test_product_details[PRICE])
        self.assertEqual(product.num_in_stock, test_product_details[NUM_IN_STOCK])

        self.client.logout()


    def test_customer_cannot_add_products(self):
        """
        Verify that an ordinary customer cannot add a product.
        """
        SKU = "sku"
        NAME = "name"
        DESCRIPTION = "description"
        PRICE = "price"
        NUM_IN_STOCK = "num_in_stock"

        test_product_details = {
            SKU: "SKU005",
            NAME: "testname",
            DESCRIPTION: "test description",
            PRICE: 9.99,
            NUM_IN_STOCK: 123
        }

        # Try to create the new product. The user should be
        # redirected to login.
        self.client.force_login(self.customer)
        response = self.client.post(
            reverse("product-management"),
            test_product_details
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.get("Location").startswith("login"))

        # Make sure the product did not get created.
        try:
            product = Product.objects.get(sku=test_product_details[SKU])
            self.assertIsNone(product)
        except Product.DoesNotExist:
            pass

        self.client.logout()