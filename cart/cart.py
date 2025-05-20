from store.models import Product, Profile


class Cart:
    '''
    A shopping cart class that handles the cart logic
    '''
    def __init__(self, request):
        self.session = request.session
        #Get request
        self.request = request

        # Get the current session key if it exits
        cart = self.session.get('session_key')

        # if the user is new, no session key! Create one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages of sites
        self.cart = cart

    def db_add(self,product,quantity):
        product_id = str(product)
        product_qty = str(quantity)
        # Logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Login cart
        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # dictionary to str
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            # save carty to the profile model
            current_user.update(old_cart=str(carty))


    def add(self, product,quantity):
        product_id = str(product.id)
        product_qty= str(quantity)
        # Logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        # Login cart
        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # dictionary to str
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            # save carty to the profile model
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        # Get product ids from cart
        product_ids = self.cart.keys()
        #lookup those key in our product database model
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        # start counting at 0
        total = 0
        for key,value in quantities.items():
            # convert key string into int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total += product.sale_price * value
                    else:
                        total += product.price * value
        return total



    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # Get ids from cart
        product_ids = self.cart.keys()
        #Use ids tp lookup products in database model
        products = Product.objects.filter(id__in=product_ids)
        # return those lookup products
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product.id)
        product_qty = int(quantity)

        # Update dictionary/cart
        self.cart[product_id] = product_qty
        self.session.modified = True

        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # dictionary to str
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            # save carty to the profile model
            current_user.update(old_cart=str(carty))

        return self.cart

    def delete(self, product):
        product_id= str(product)
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        if self.request.user.is_authenticated:
            # get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # dictionary to str
            carty = str(self.cart)
            carty = carty.replace("'", '"')
            # save carty to the profile model
            current_user.update(old_cart=str(carty))
