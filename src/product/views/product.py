import sys
from rest_framework.response import Response
from django.forms.models import inlineformset_factory
from django.shortcuts import redirect, render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.views import generic
from django.views.generic.list import ListView
from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from product.forms import ProductForm, ProductUpdateForm, ProductUpdateFormset

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())

        print(self.request.POST)
        return context


class ProductCreateAPI(APIView):

    def post(self, request):
        print(request.data)

        data = {}
        data['title'] = request.data['title']
        data['sku'] = request.data['sku']
        data['description'] = request.data['description']
        data['product_variant_prices'] = request.data['product_variant_prices']

        if not data['title']:
            return Response({'bad request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            product = Product()
            product.title = data['title']
            product.sku = data['sku']
            product.description = data['description']
            product.save()
        
        for value in data['product_variant_prices']:
            product_variant_list = value['title'].split('/')
            product_variant_list.pop()

            product_variant_price = ProductVariantPrice()

            for index, item in enumerate(product_variant_list):
                print(index, item)

                if index == 0:
                    color_object = Variant.objects.get(title='Color')
                    try:
                        product_variant_one = ProductVariant.objects.get(variant_title=item, variant=color_object, product=product) 
                    except:
                        product_variant_one = ProductVariant.objects.create(variant_title=item, variant=color_object, product=product)
                        product_variant_one.save()

                    product_variant_price.product_variant_one = product_variant_one
                
                if index == 1:
                    size_object = Variant.objects.get(title='Size')
                    try:
                        product_variant_two = ProductVariant.objects.get(variant_title=item, variant=size_object, product=product) 
                    except:
                        product_variant_two = ProductVariant.objects.create(variant_title=item, variant=size_object, product=product)
                        product_variant_two.save()

                    product_variant_price.product_variant_two = product_variant_two
                
                if index == 2:
                    style_object = Variant.objects.get(title='Style')
                    try:
                        product_variant_three = ProductVariant.objects.get(variant_title=item, variant=style_object, product=product) 
                    except:
                        product_variant_three = ProductVariant.objects.create(variant_title=item, variant=style_object, product=product)
                        product_variant_three.save()
                    
                    product_variant_price.product_variant_three = product_variant_three
            product_variant_price.stock = value['stock']
            product_variant_price.price = value['price']
            product_variant_price.product = product
            product_variant_price.save()
        return Response({'product created successfully'}, status=status.HTTP_200_OK)


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
    formset = inlineformset_factory(Product, ProductVariantPrice, form=ProductUpdateForm, formset=ProductUpdateFormset, extra=1, can_delete=True)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id=id)
            product.title= form.cleaned_data['title']
            product.sku = form.cleaned_data['sku']
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
