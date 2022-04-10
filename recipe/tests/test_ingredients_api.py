from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient #Имитируем улиент АПИ
from rest_framework import status #Статуст коды для http

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    """Тетс на доступность API ингредиентов"""
    def setUp(self):
        self.client = APIClient()
        
    def test_login_reqired(self):
        """Тест на необходимость аунтефикации"""
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateIngredientsApiTests(TestCase):
    """Тест на получение ингредиентов авторизированным пользователем"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@admin.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_ingredient_list(self):
        """Тест на получение списка ингредиентов"""
        Ingredient.objects.create(user=self.user, name='kete')
        Ingredient.objects.create(user=self.user, name='Salt')
        
        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many= True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_ingredients_limited_to_user(self):
        """Проверка на возвращение ингредиентов только для авторизированного пользователя"""
        user2 = get_user_model().objects.create_user(
            'other@admin.com',
            'testpass'
        )        
        Ingredient.objects.create(user = user2, name='Уксус')
        
        ingridient = Ingredient.objects.create(user = self.user, name='Куркума')
        
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingridient.name)
        
    def test_create_ingredient_successful(self):
        """Тетс на создание нового ингредиента"""
        payload = {'name':'Кабачок'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Тетс на создание нового ингредиента с неккоректными данными"""
        payload = {'name':''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        

