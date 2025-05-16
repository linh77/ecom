import json

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q

from cart.cart import Cart
from payment.models import ShippingAddress
from .forms import UpdateUserForm, ChangePasswordForm, UserInfoForm, LoginForm, RegisterForm
from .models import Product, Category, Profile
from payment.forms import ShippingAddressForm


def search(request):
    '''
    Search for products in the database based on the search term provided by the user.

    '''
    # Determine if they filled out the search form
    if request.method == 'POST':
        searched = request.POST['searched']

        # Query the database
        searched_products = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if searched_products:
            messages.success(request, f'You have searched for "{searched}"')
        else:
            messages.error(request, f'No products found for "{searched}"')

        return render(request, 'store/search.html', {'searched': searched, 'products': searched_products})

    else:
        return render(request, 'store/search.html')


def home(request):
    '''
    Render the home page with a list of all products.
    '''
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})


def about(request):
    '''
    render the about page.
    '''
    return render(request, 'store/about.html', {})


def logout_user(request):
    '''
    Log the user out and redirect to the home page with a success message.
    '''
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')


def register_user(request):
    '''
    Render the registration page and handle user registration.
    '''
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
                return redirect('update_info')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('register')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html',
                  {'form': form})  # This line should not be indented under the else block


def update_user(request):
    '''
    Render the update user page and handle user information updates.
    '''
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to update your account')
        return redirect('login')

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UpdateUserForm(instance=request.user)

    return render(request, 'store/update_user.html', {
        'user_form': form
    })


def update_password(request):
    '''
    Render the update password page and handle password updates.
    '''
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to update your password')
        return redirect('login')

    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your password has been updated successfully. Please log in again.')
                logout(request)
                return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred while updating your password.')
                return redirect('update_password')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'store/update_password.html', {'form': form})


def update_info(request):
    '''
    Render the update information page and handle user information updates.
    '''
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user, created = ShippingAddress.objects.get_or_create(
            user=request.user,
            defaults={
                'shipping_full_name': current_user.user.username,
                'shipping_email': current_user.user.email,
                'shipping_address1': '',
                'shipping_address2': '',
                'shipping_city': '',
                'shipping_state': '',
                'shipping_zipcode': '',
                'shipping_country': ''
            })

        form = UserInfoForm(request.POST or None, instance=current_user)

        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your information has been updated')
            return redirect('update_info')
        return render(request, 'store/update_info.html', {'form': form,'shipping_form': shipping_form})
    else:
        messages.error(request, 'You must be logged in to update your account')
        return redirect('login')


def product(request, pk):
    '''
    Render the product page with details of a specific product.
    '''
    product = Product.objects.get(id=pk)
    return render(request, 'store/product.html', {'product': product})


def category(request, foo):
    '''
    Render the category page with products belonging to a specific category.
    '''
    # Replace hyphens with spaces
    foo = foo.replace('-', ' ')
    # Grab the category from the url
    try:
        # look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'store/category.html', {
            'category': category,
            'products': products
        })
    except:
        messages.error(request, 'Invalid category')
        return redirect('home')


def category_summary(request):
    '''
    Render the category summary page with all categories.
    '''
    categories = Category.objects.all()

    return render(request, 'store/category_summary.html', {
        'categories': categories,
    })


# views from login form

def login_user(request):
    '''
    Render the login page and handle user authentication.
    '''
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request, user)

            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            # Handle shopping cart
            try:
                current_user = Profile.objects.get(user__id=user.id)
                saved_cart = current_user.old_cart
                if saved_cart:
                    converted_cart = json.loads(saved_cart)
                    cart = Cart(request)
                    for key, value in converted_cart.items():
                        cart.db_add(product=key, quantity=value)
            except Profile.DoesNotExist:
                pass  # Handle case where profile doesn't exist

            messages.success(request, f'Welcome to Changiu, {user.username}!')
            return redirect('home')

    else:
        form = LoginForm()

    return render(request, 'store/login.html', {
        'form': form,
        'title': 'Login'
    })
