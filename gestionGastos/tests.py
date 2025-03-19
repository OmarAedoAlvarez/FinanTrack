from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

#Prueba para validar el correcto funcionamiento del registro de usuarios
class UserRegistrationTestCase(TestCase):
  def test_user_registration(self):
    # Datos del formulario de registro
    data = {
      'username': 'dummieUser',
      'password1': 'securepassword123',
      'password2': 'securepassword123'
    }
    # Enviar una solicitud POST al formulario de registro
    response = self.client.post(reverse('register'), data)

    # Verificar que el registro fue exitoso
    self.assertEqual(response.status_code, 302)  
    self.assertRedirects(response, reverse('login'))  

    # Verificar que el usuario ha sido creado en la base de datos
    user = User.objects.get(username='dummieUser')
    self.assertIsNotNone(user)
    self.assertTrue(user.check_password('securepassword123'))  
  
class UserLoginTestCase(TestCase):
    def test_user_login(self):
        user = User.objects.create_user(username='dummieUser', password='securepassword123')
        response = self.client.post(reverse('login'), {
            'username': 'dummieUser',
            'password': 'securepassword123'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('home'))  

