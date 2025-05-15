from .cart import Cart

# Create context processor so shopping cart can work on all page

def cart(request):
    return {'cart': Cart(request)}