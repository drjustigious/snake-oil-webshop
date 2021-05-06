from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from snakeoil_webshop.models import Product

class Command(BaseCommand):

    help = "Create a set of dummy products suitable for demonstration purposes. Existing products with overlapping SKUs will be removed."

    def handle(self, *args, **options):
        """
        Create four different types of snake oil.
        First remove any products with conflicting SKUs.
        """
        demo_products = [
            {
                "sku": "SKU001",
                "name": "Clear snake oil",
                "description": "A clear liquid potentially possessing some aspects of the the essence of the regenerative properties of snake oil.",
                "price": "11.99",
                "num_in_stock": "108"
            },
            {
                "sku": "SKU002",
                "name": "Turbid snake oil",
                "description": "A rather opaque extract from who knows what part of some venomous snake, likely from a deep jungle somewhere far away.",
                "price": "16.99",
                "num_in_stock": "273"
            },
            {
                "sku": "SKU003",
                "name": "Thick snake oil",
                "description": "A viscous slime with a rather alarming aroma. Might be flammable enough to pose a moderate danger indoors.",
                "price": "27.99",
                "num_in_stock": "35"
            },
            {
                "sku": "SKU004",
                "name": "Potent snake oil",
                "description": "This actively bubbling mixture of unknown biochemical agents will almost certainly cure all disese and illness that it by itself does not cause.",
                "price": "33.99",
                "num_in_stock": "1899"
            }
        ]

        for product_definition in demo_products:
            # Delete any old product with a conflicting SKU.
            try:
                product = Product.objects.get(sku=product_definition["sku"])
                product.delete()
            except Product.DoesNotExist:
                pass

            # Create a new demo product.
            product = Product.objects.create(**product_definition)
            self.stdout.write(self.style.SUCCESS(f"Demo product created: {product.sku} - {product.name}."))