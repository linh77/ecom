from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

from store.models import Product
from .cart import Cart


def cart_summary(request):
    # Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    return render(request, 'cart/cart_summary.html', {
        'cart_products': cart_products,
        'cart': cart,
        'quantities': quantities,
        'totals': totals
    })


def cart_add(request):
    # Get the cart
    cart = Cart(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # Lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        # Save to session
        cart.add(product=product, quantity=product_qty)
        # Get cart quantity
        cart_quantity = cart.__len__()

        # return respone
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, 'Product added to cart')
        return response
    else:
        return JsonResponse({'error': 'Request not valid'})


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        # Call delete Function
        cart.delete(product_id)
        response = JsonResponse({'deleted': True})
        messages.success(request, 'Product deleted from cart')
        return response

    return redirect('cart_summary')


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('product_id'))
            product_qty = int(request.POST.get('product_qty'))

            # Get the product object
            product = get_object_or_404(Product, id=product_id)

            # Update the cart
            cart.update(product=product, quantity=product_qty)

            response = JsonResponse({'qty': product_qty})
            messages.success(request, 'Product quantity updated')
            return response
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity or product ID'}, status=400)

    return redirect('cart_summary')
