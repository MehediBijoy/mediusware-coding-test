import sys
from django.forms.models import inlineformset_factory
from django.shortcuts import redirect, render
from django.db.models import Q
from django.views import generic
from django.views.generic.list import ListView
from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from product.forms import ProductForm

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())

        print(self.request.POST)
        return context


class ProductList(ListView):
    model = Product
    paginate_by = 5

    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['colors'] = ProductVariant.objects.filter(variant__title='Color').values('variant_title').distinct()
        context['sizes'] = ProductVariant.objects.filter(variant__title='Size').values('variant_title').distinct()
        context['styles'] = ProductVariant.objects.filter(variant__title='Style').values('variant_title').distinct()
        return context


def ProductSearch(request):
    data = {}
    if request.method == 'POST':
        data['title'] = request.POST['title']
        data['variant'] = request.POST['variant']
        data['price_from'] = request.POST['price_from']
        data['price_to'] = request.POST['price_to']

        if data['title'] or data['variant'] or data['price_from'] or data['price_to']:
            product = Product.objects.all()
            if data['title']:
                product = product.filter(title__contains=data['title'])

            if data['variant']:
                product = product.filter(Q(product_variant__product_variant_one__variant_title=data['variant']) | 
                                        Q(product_variant__product_variant_two__variant_title=data['variant']) | 
                                        Q(product_variant__product_variant_three__variant_title=data['variant'])).distinct()

            if data['price_from'] or data['price_to']:
                start = int(data['price_from']) if data['price_from'] else 0
                end = int(data['price_to']) if data['price_to'] else sys.maxsize
                product = product.filter(product_variant__price__range=(start, end)).distinct()

            return render(request, 'products/search-result.html', {'products': product})
        else:
            return render(request, 'products/search-result.html', {'products': None})

def updateProduct(request, id):
    context = {}
    product = Product.objects.get(id=id)
    formset = inlineformset_factory(Product, ProductVariantPrice, 
            fields=('product_variant_one', 'product_variant_two', 'product_variant_three', 'price', 'stock'), 
            extra=1, can_delete=True)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=id)
            product.title= form.cleaned_data['title']
            product.description = form.cleaned_data['description']
            product.save()
        
        variant_formset = formset(request.POST, instance=product)
        if variant_formset.is_valid():
            variant_formset.save(commit=True)
        return redirect('product:list.product')
    else:
        context['product_form'] = ProductForm(instance=product)
        context['variants'] = formset(instance=product)

    return render(request, 'products/update-product.html', context)
