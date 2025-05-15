from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)


# Mix profile and user
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend user admin model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    inlines = [ProfileInline]

# Unregister the original user admin
admin.site.unregister(User)

# Register the new UserAdmin
admin.site.register(User, UserAdmin)