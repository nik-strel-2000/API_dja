from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework.test import APIClient #Имитируем улиент АПИ
from rest_framework import status #Статуст коды для http

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Возвращение ЮРЛ для просмотра рецепта"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Основное блюдо'):
    """Создание и возвращение экземпляра тега"""
    return Tag.objects.create(user=user,name=name)

def sample_ingredient(user, name='Корица'):
    """Создание и возвращение экземпляра ингредиента"""
    return Ingredient.objects.create(user=user,name=name)


def sample_recipe(user, **params):
    """Создание и возвращение экземпляра рецепта"""
    defaults = {
        'title':'Пример рецепта',
        'time_minutes':10,
        'price':5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """Тест апи не авторизованного пользователя"""
    def setUp(self):
        self.client = APIClient()
        
    def test_reqired_auth(self):
        """Тест на необходимость аунтефикации"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Тест апи авторизованного пользователя"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@admin.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipe(self):
        """Тест на вывод списка рецептов"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_recipe_limited_to_user(self):
        """Тетс на вывод рецептов пользователя"""
        user2 = get_user_model().objects.create_user(
            'other@admin.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        
    def test_view_recipe_detail(self):
        """Тетстовый проссмотр сведений о рецепте"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        
    def test_create_basic_recipe(self):
        """Тест на создание рецепта"""
        payload = {
            'title': 'Шоколадный шейк',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
            
    def test_create_recipe_with_tags(self):
        """Тест на создание рецепта с тегами"""
        tag1 = sample_tag(user=self.user, name='Веган')
        tag2 = sample_tag(user=self.user, name='Десерт')
        payload = {
            'title': 'Авокадо & Апельсин',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        
    def test_create_recipe_with_ingredients(self):
        """Тест на создание рецепта с ингредиентами"""
        ingredient1 = sample_ingredient(user=self.user, name='Креветки')
        ingredient2 = sample_ingredient(user=self.user, name='Имбирь')
        payload = {
            'title':'Тайское красное карри с креветками',
            'ingredients':[ingredient1.id,ingredient2.id],
            'time_minutes':80,
            'price':800.00
        }
        res = self.client.post(RECIPES_URL, payload )
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        
    def test_partial_update_recipe(self):
        """Тест на обновление рецепта методом Patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Карри')
        
        payload = {'title':'Куриная тикка', 'tags':[new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
    
    def test_full_update_recipe(self):
        """Тест на обновление рецепта с методом put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Карбонара',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
        
        