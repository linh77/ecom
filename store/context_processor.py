from .models import Category

def navbar_category(request):
    return {'navbar_category': Category.objects.all()}