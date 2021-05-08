from django import forms
from django.db.models import Q

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import widgets

from snakeoil_webshop.models import Product


class ProductSearchForm(forms.Form):
    """
    A simple form for searching products by SKU (product code) or name.
    Allows the user to choose whether to sort the results by price or name.
    """
    #############
    # CONSTANTS #
    #############

    # Constants for sorting options.
    NAME_ASC = "name"
    NAME_DESC = "-name"
    PRICE_ASC = "price"
    PRICE_DESC = "-price"

    SORTING_CHOICES = [
        (NAME_ASC, "Name, A-Z"),
        (NAME_DESC, "Name, Z-A"),
        (PRICE_ASC, "Price, low first"),
        (PRICE_DESC, "Price, high first"),
    ]


    #################
    # SEARCH FIELDS #
    #################

    # A substring search field that will hit the SKU or name of a product.
    search_string = forms.CharField(
        label="Search products",
        required=False,
        help_text="Search for products by name or product code."
    )

    # A list of available ways to sort the results.
    sort_by = forms.ChoiceField(
        label="Sort by",
        required=True,
        choices=SORTING_CHOICES
    )


    ###########
    # METHODS #
    ###########

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'List products', css_class='btn-success'))    


    def filter_results(self):
        """
        Assuming this form has bound data, return the products
        that match the search criteria entered into the form.
        """
        if not self.is_valid():
            # Return nothing if the query was invalid.
            # This should allow the form page to reload
            # quickly to show the validation errors.
            return Product.objects.none()

        results = Product.objects.all()            

        search_string = self.cleaned_data.get("search_string", "")
        if search_string:
            q = Q(sku__icontains=search_string) | Q(name__icontains=search_string)
            results = results.filter(q)

        sort_by = self.cleaned_data.get("sort_by", self.NAME_ASC)
        results = results.order_by(sort_by)

        return results


    def give_all_results(self):
        """
        Return all products that are for sale.
        Called when a fresh empty form is presented
        to the user.
        """
        results = Product.objects.all().order_by(self.NAME_ASC)

        return results



class ProductCreationForm(forms.ModelForm):
    """
    This form collects the details necessary for adding a new
    product into the web shop's database.
    """
    class Meta:
        model = Product
        fields = [
            'sku',
            'name',
            'description',
            'price',
            'num_in_stock',
        ]
        labels = {
            "sku": "Product code",
            "num_in_stock": "Number of items in stock"
        }
        widgets = {
            "name": forms.TextInput
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Add product', css_class='btn-success'))


    def clean_price(self):
        """
        Make sure the given price isn't negative.
        """
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("The price of a product cannot be negative.")

        return price


    def clean_num_in_stock(self):
        """
        Make sure the given number of items in stock isn't negative.
        """
        num_in_stock = self.cleaned_data.get("num_in_stock")
        if num_in_stock < 0:
            raise forms.ValidationError("The stock count of a product cannot be negative.")

        return num_in_stock


    def give_all_results(self):
        """
        Return all product definitions in the reverse update order,
        i.e. the last product modified comes up first.
        """
        results = Product.objects.all().order_by('-updated')

        return results



class AddToCartForm(forms.Form):
    """
    A lightweight form for validating requests to add a product
    to the shopping cart.
    """
    # The product ID.
    pk = forms.IntegerField()
    # How many items to add?
    num_items = forms.IntegerField(required=False)