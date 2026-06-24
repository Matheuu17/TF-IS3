from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Pedido, Producto, Profile
import json

class YapeIntegrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user with Mozo role
        self.user = User.objects.create_user(username='mozo_test@ebs.pe', email='mozo_test@ebs.pe', password='password123')
        self.profile = self.user.profile
        self.profile.rol = 3  # Mozo
        self.profile.save()

        # Create products
        self.burger = Producto.objects.create(nombre='Hamburguesa Suprema', precio=18.50)
        self.fries = Producto.objects.create(nombre='Papas Fritas Medianas', precio=7.00)

        # Create a delivered order
        self.pedido = Pedido.objects.create(
            user=self.user,
            mesa=3,
            estado=Pedido.EstadoPedido.ENTREGADO,
            descripcion='Nota especial'
        )
        self.pedido.productos.add(self.burger, self.fries)
        self.pedido.save()

    def test_generar_qr_yape_success(self):
        self.client.login(username='mozo_test@ebs.pe', password='password123')
        url = reverse('generar_qr_yape')
        payload = {'pedido_id': self.pedido.id, 'propina': 3.50}
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('qr_url', data)
        self.assertIn('payment_id', data)
        self.assertTrue(data['payment_id'].startswith('mp_mock_'))
        
        # Verify that the propina has been updated on the Pedido in BBDD
        self.pedido.refresh_from_db()
        self.assertEqual(float(self.pedido.propina), 3.50)

    def test_generar_qr_yape_missing_id(self):
        self.client.login(username='mozo_test@ebs.pe', password='password123')
        url = reverse('generar_qr_yape')
        payload = {}
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)

    def test_obtener_estado_pedido(self):
        self.client.login(username='mozo_test@ebs.pe', password='password123')
        url = reverse('obtener_estado_pedido', kwargs={'pedido_id': self.pedido.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['estado'], 'ENTREGADO')

    def test_webhook_mercadopago_mock_success(self):
        url = reverse('webhook_mercadopago')
        payload = {
            'action': 'payment.created',
            'data': {
                'id': f'mp_mock_{self.pedido.id}'
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
        
        # Verify database update
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'PAGADO')
        self.assertIsNotNone(self.pedido.datecompleted)

    def test_webhook_mercadopago_failed_state(self):
        url = reverse('webhook_mercadopago')
        payload = {
            'action': 'payment.created',
            'data': {
                'id': '123456789'
            },
            'status': 'rejected',
            'metadata': {
                'pedido_id': str(self.pedido.id)
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'No processing needed')
        
        # Verify database was not updated to PAGADO
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'ENTREGADO')
