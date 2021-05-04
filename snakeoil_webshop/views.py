from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from snakeoil_webshop.forms import ProductSearchForm
from snakeoil_webshop.models import Product


class ShopView(LoginRequiredMixin, TemplateView):
    
    template_name = "shop.html"

    login_url = '/login/'
    redirect_field_name = 'next'


    def get_context_data(self, *args, **kwargs):
        context = super(ShopView, self).get_context_data(*args, **kwargs)

        if self.request.method == 'POST':
            # We received a filled product search form from the user.
            form = ProductSearchForm(self.request.POST)
            products = form.filter_results()
        else:
            # We're serving the shop page out for the first time with an empty search form.
            form = ProductSearchForm()
            products = form.give_all_results()

        added_context = {
            "form": form,
            "products": products
        }
        context.update(added_context)

        return context


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)