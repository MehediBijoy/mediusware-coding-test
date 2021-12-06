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

        product = Product.objects.all()
        if data['title']:
            product = product.filter(title__contains=data['title'])
        product = ProductVariantPrice.objects.filter(product__in=product)

        if data['variant']:
            product = product.filter(Q(product_variant_one__variant_title=data['variant']) | 
                                                    Q(product_variant_two__variant_title=data['variant']) | 
                                                    Q(product_variant_three__variant_title=data['variant']))

        if data['price_from'] or data['price_to']:
            start = int(data['price_from']) if data['price_from'] else 0
            end = int(data['price_to']) if data['price_to'] else 0
            product = product.filter(price__range=(start, end))
            
    return render(request, 'products/search-result.html', {'products': product})


def updateProduct(request, id):
    context = {}
    if request.method == 'POST':
        print(request.POST)
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=id)
            product.title= form.cleaned_data['title']
            product.description = form.cleaned_data['description']
            product.save()
        
        return redirect('product:list.product')
    else:
        product = Product.objects.get(id=id)
        context['product_form'] = ProductForm(instance=product)

    return render(request, 'products/update-product.html', context)
