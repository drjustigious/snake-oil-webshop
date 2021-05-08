import secrets

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission


class Command(BaseCommand):
    PASSWORD_LENGTH = 16

    STAFF_USERNAME = "demo.webmaster"
    MANAGER_USERNAME = "demo.manager"
    CUSTOMER_X_USERNAME = "demo.customer.x"
    CUSTOMER_Y_USERNAME = "demo.customer.y"
    CUSTOMER_Z_USERNAME = "demo.customer.z"

    MANAGERS_GROUP_NAME = "shop.managers"
    STAFF_GROUP_NAME = "shop.staff"

    SILENT = "silent"

    help = (
        "Sets up a staff user, a shop manager and three customers with the correct permissions "
        "for demo purposes. All accounts will receive new random passwords. The passwords will "
        "be printed out in plain text!"
    )

    def handle(self, *args, **options):
        # Create the staff user. They have full access to webshop functions and the Django Admin.
        staff_user = self.update_user(self.STAFF_USERNAME, options)
        self.give_staff_permissions(staff_user)

        # Create the shop manager. They have full webshop feature access, but can't see Django Admin.
        # This part also configures the shop manager permission group.
        shop_manager = self.update_user(self.MANAGER_USERNAME, options)
        manager_group, created = Group.objects.get_or_create(name=self.MANAGERS_GROUP_NAME)
        manager_group.permissions.add(
            Permission.objects.get(codename="add_product")
        )
        manager_group.user_set.add(shop_manager)

        # Create three ordinary web shop customer accounts.
        self.update_user(self.CUSTOMER_X_USERNAME, options)
        self.update_user(self.CUSTOMER_Y_USERNAME, options)
        self.update_user(self.CUSTOMER_Z_USERNAME, options)

        if not options.get(self.SILENT, False):
            self.stdout.write(self.style.SUCCESS("Demo login accounts created and/or updated with new passwords."))


    def update_user(self, username, options):
        """
        Changes the given user's password, or creates the user
        if they don't exist.

        Returns the updated or created user.
        """
        user, created = User.objects.get_or_create(username=username)
        password = secrets.token_urlsafe(self.PASSWORD_LENGTH)
        if not options.get(self.SILENT, False):
            self.stdout.write(self.style.NOTICE(f"{user.username.ljust(16)}: {password}"))
        user.set_password(password)
        user.save()

        return user


    @staticmethod
    def give_staff_permissions(user):
        """
        Promotes the given user to a staff member with full
        privileges over the web shop's resources.
        """
        # Create a staff user group if it didn't exist yet.
        staff_group, created = Group.objects.get_or_create(name=Command.STAFF_GROUP_NAME)

        # Give the staff group all permissions over the webshop resources.
        nouns = ["product", "shoppingcart", "shoppingcartitem"]
        verbs = ["add", "change", "delete", "view"]

        for noun in nouns:
            for verb in verbs:
                permission_codename = f"{verb}_{noun}"
                staff_group.permissions.add(
                    Permission.objects.get(codename=permission_codename)
                )

        # Add the given user to the staff group.
        staff_group.user_set.add(user)                
        user.is_staff = True
        user.save()