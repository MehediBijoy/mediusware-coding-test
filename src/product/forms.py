from django.forms import ModelForm, CharField, TextInput, Textarea, CheckboxInput, BaseInlineFormSet
from product.models import Product, ProductVariantPrice, Variant, ProductVariant


class VariantForm(ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input', 'id': 'active'})
        }


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'sku', 'description']


class ProductUpdateForm(ModelForm):
    color = CharField(label='Color', max_length=20, required=False)
    size = CharField(label='Size', max_length=20, required=False)
    style = CharField(label='Style', max_length=20, required=False)

    class Meta:
        model = ProductVariantPrice
        fields = ['color', 'size', 'style', 'price', 'stock']

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)

        try:
            self.product_color = ProductVariant.objects.get(id=self.instance.product_variant_one_id).variant_title
        except ProductVariant.DoesNotExist:
            self.product_color = None
        
        try:
            self.product_size = ProductVariant.objects.get(id=self.instance.product_variant_two_id).variant_title
        except ProductVariant.DoesNotExist:
            self.product_size = None

        try:
            self.product_style = ProductVariant.objects.get(id=self.instance.product_variant_three_id).variant_title
        except ProductVariant.DoesNotExist:
            self.product_style = None

        self.fields['color'].initial = self.product_color
        self.fields['size'].initial = self.product_size
        self.fields['style'].initial = self.product_style


class ProductUpdateFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms: 
            try:
                self.color = form.cleaned_data['color']
                self.size = form.cleaned_data['size']
                self.style = form.cleaned_data['style']
                self.product = form.cleaned_data['product']
            except KeyError:
                self.color = None
                self.size = None
                self.style = None
                self.product = None

            if self.color:
                variant = Variant.objects.get(title='Color')
                try:
                    product_variant = ProductVariant.objects.get(variant_title=self.color, variant=variant, product=self.product)
                    form.instance.product_variant_one = product_variant
                    form.instance.save()
                except:
                    product_variant = ProductVariant.objects.create(variant_title=self.color, variant=variant, product=self.product)
                    form.instance.product_variant_one = product_variant
                    form.instance.save()
            
            if self.size:
                variant = Variant.objects.get(title='Color')
                try:
                    product_variant = ProductVariant.objects.get(variant_title=self.size, variant=variant, product=self.product)
                    form.instance.product_variant_two = product_variant
                    form.instance.save()
                except:
                    product_variant = ProductVariant.objects.create(variant_title=self.size, variant=variant, product=self.product)
                    form.instance.product_variant_two = product_variant
                    form.instance.save()
                    
            if self.style:
                variant = Variant.objects.get(title='Style')
                try:
                    product_variant = ProductVariant.objects.get(variant_title=self.style, variant=variant, product=self.product)
                    form.instance.product_variant_three = product_variant
                    form.instance.save()
                except:
                    product_variant = ProductVariant.objects.create(variant_title=self.style, variant=variant, product=self.product)
                    form.instance.product_variant_three = product_variant
                    form.instance.save()
            
