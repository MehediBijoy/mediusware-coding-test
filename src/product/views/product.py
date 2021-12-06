from django.views import generic
from django.views.generic.list import ListView
from product.models import Variant, Product, ProductVariant


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
        context['colors'] = ProductVariant.object.colors().values('variant_title').distinct()
        context['sizes'] = ProductVariant.object.sizes().values('variant_title').distinct()
        context['styles'] = ProductVariant.object.styles().values('variant_title').distinct()
        return context
