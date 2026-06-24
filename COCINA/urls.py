"""
URL configuration for SUSALUD project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin, name = 'signin'),
    path('signup/', views.signup, name = 'signup'),
    path('pedidos/', views.pedidos, name = 'pedidos'),
    path('pedidos_completed', views.pedidos_completed, name = 'pedidos_completed'),
    path('pedidos/create/', views.create_pedido, name = 'create_pedido'),
    path('pedidos/<int:pedido_id>/', views.pedido_detail, name = 'pedido_detail'),
    path('pedidos/<int:pedido_id>/complete', views.complete_pedido, name = 'complete_pedido'),
    path('pedidos/<int:pedido_id>/delete', views.delete_pedido, name = 'delete_pedido'),
    path('logout/', views.signout, name = 'logout'),
    path('signin/', views.signin, name = 'signin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/exportar-excel/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('404/', views.handler404, name='404'),
    path('producto/<int:producto_id>/cambiar_disponibilidad/', views.cambiar_disponibilidad, name='cambiar_disponibilidad'),
    path('producto/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:producto_id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('cocina', views.crear_producto, name='crear_producto'),
    path('pedidos/<int:pedido_id>/update/<str:nuevo_estado>', views.update_estado, name='update'),
    path('pedidos/<int:pedido_id>/cancel/', views.cancelar_pedido, name='cancelar_pedido'),
    path('mozo/pedido/generar-qr/', views.generar_qr_yape, name='generar_qr_yape'),
    path('webhook/mercadopago/', csrf_exempt(views.webhook_mercadopago), name='webhook_mercadopago'),
    path('mozo/pedido/<int:pedido_id>/estado/', views.obtener_estado_pedido, name='obtener_estado_pedido'),
]
