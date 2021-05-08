from snakeoil_webshop.models import ShoppingCart

def find_active_cart_for_user(user):
    """
    Returns the active ShoppingCart of the given User.
    Right now every user has at most just one cart,
    so we will also create a cart here if it does not
    exist yet.
    """
    active_cart, created = ShoppingCart.objects.get_or_create(user=user)
    return active_cart
