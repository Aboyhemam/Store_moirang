from .models import Cart

def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.items.count()
    return {'cart_count': count}
