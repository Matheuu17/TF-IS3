from django.contrib import admin
from .models import Pedido, Profile


class PedidoAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

# Register your models here.
admin.site.register(Pedido, PedidoAdmin)

admin.site.register(Profile)

