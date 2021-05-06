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