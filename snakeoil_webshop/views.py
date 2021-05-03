from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class ShopView(LoginRequiredMixin, TemplateView):
    
    template_name = "shop.html"

    login_url = '/login/'
    redirect_field_name = 'next'