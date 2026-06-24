from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Pedido, Producto, Profile

class PedidoForm(ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'mesa', 'productos', 'descripcion']
        widgets = {
            'mesa': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
            'productos': forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox h-5 w-5 text-orange-500 border-gray-300 rounded focus:ring-orange-500 dark:border-gray-600 dark:bg-gray-700 dark:checked:bg-orange-500'}),
            'descripcion': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-xl border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'rows': 3}),
            'cliente': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
        }

    def __init__(self, *args, **kwargs):
        super(PedidoForm, self).__init__(*args, **kwargs)
        self.fields['productos'].queryset = Producto.objects.all()
        self.fields['cliente'].queryset = User.objects.filter(profile__rol=2)
        self.fields['cliente'].empty_label = "--- Invitado ---"
        self.fields['cliente'].required = False
        
        # Filtrar mesas ocupadas
        pedidos_activos = Pedido.objects.filter(datecompleted__isnull=True)
        if self.instance and self.instance.pk:
            pedidos_activos = pedidos_activos.exclude(pk=self.instance.pk)
            
        mesas_ocupadas = pedidos_activos.values_list('mesa', flat=True)
        mesas_disponibles = [
            (numero, nombre) for numero, nombre in Pedido.Mesa.choices
            if numero not in mesas_ocupadas
        ]
        self.fields['mesa'].choices = mesas_disponibles

    def clean_productos(self):
        productos = self.cleaned_data.get('productos')
        if productos:
            for prod in productos:
                if not prod.disponible:
                    raise forms.ValidationError(f"El plato '{prod.nombre}' no está disponible actualmente.")
        return productos

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'disponible']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'placeholder': 'Ej. Hamburguesa'}),
            'precio': forms.NumberInput(attrs={'class': 'w-full rounded-xl border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white', 'step': '0.01'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-orange-500 border-gray-300 rounded focus:ring-orange-500 dark:border-gray-600 dark:bg-gray-700 dark:checked:bg-orange-500'}),
        }