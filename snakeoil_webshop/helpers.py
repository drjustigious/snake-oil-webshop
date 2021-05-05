from snakeoil_webshop.models import ShoppingCart

def find_active_cart_for_user(user):
    """
    Returns the active ShoppingCart of the given User.
    Right now every user has at most just one cart.
    """
    try:
        active_cart = ShoppingCart.objects.get(user=user)
        return active_cart
    except ShoppingCart.DoesNotExist:
        return None
