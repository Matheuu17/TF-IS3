from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)  # Determinado por el cocinero, pero por defecto siempre estará disponible

    def __str__(self):
        return f"{self.nombre} - S/. {self.precio} ({'Disponible' if self.disponible else 'Agotado'})"

class Pedido(models.Model):
    # Definición de estados
    class EstadoPedido(models.TextChoices):
        CREADO = 'CREADO', 'Pedido creado'
        PREPARACION = 'PREPARACION', 'En preparación'
        LISTO = 'LISTO', 'Listo'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        COBRADO = 'COBRADO', 'Cobrado'
        PAGADO = 'PAGADO', 'Pagado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    class Mesa(models.IntegerChoices):
        MESA_1 = 1, 'Mesa 1'
        MESA_2 = 2, 'Mesa 2'
        MESA_3 = 3, 'Mesa 3'
        MESA_4 = 4, 'Mesa 4'
        MESA_5 = 5, 'Mesa 5'
        MESA_6 = 6, 'Mesa 6'
        MESA_7 = 7, 'Mesa 7'
        MESA_8 = 8, 'Mesa 8'
        MESA_9 = 9, 'Mesa 9'
        MESA_10 = 10, 'Mesa 10'
    mesa = models.IntegerField(choices=Mesa.choices, default=Mesa.MESA_1)
    estado = models.CharField(max_length=20, choices=EstadoPedido.choices, default=EstadoPedido.CREADO)
    # Relación muchos a muchos para los platos del pedido
    productos = models.ManyToManyField(Producto) 
    descripcion = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(User, related_name='pedidos_cliente', on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    propina = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido Mesa {self.mesa}"

    @property
    def get_total(self):
        return sum(producto.precio for producto in self.productos.all())

    @property
    def get_puntos(self):
        return int(self.get_total * Decimal('0.10'))

class Profile(models.Model):
    # Definimos los roles que podrá tener los usuarios
    ROLES = (
        (1, 'Administrador'),
        (2, 'Cliente'),
        (3, 'Mozo'),
        (4, 'Cocinero')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.IntegerField(choices=ROLES, default=2)
    def __str__(self):
        return f"{self.user.username} - {self.rol}"

@receiver(post_save, sender=User) # Cada vez que se cree un usuario, automaticamente se asignara el rol de CLIENTE, a menos que el admin lo cambie
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, rol=2)