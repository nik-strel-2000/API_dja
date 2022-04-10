from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient #Имитируем улиент АПИ
from rest_framework import status #Статуст коды для http

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """Тест на доступность API тегов"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Тест  что для получения тегов требуется логин"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Тесты для аторизованных пользователей"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'nikita.strel.2002@mail.ru',
            'nikita.strel'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Тестовое получение тегов"""
        Tag.objects.create(user=self.user, name='Овощи')
        Tag.objects.create(user=self.user, name='Десерт')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many= True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Тетс что возвращаемые теги предназначены для аунтефикацированного пользователя."""
        user2 = get_user_model().objects.create_user(
            'othet@admin.com',
            'testpass'
        )
        Tag.objects.create(user = user2, name='Фрукты')
        tag = Tag.objects.create(user = self.user, name='Привычная пища')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Тетс на создание нового тега"""
        payload = {'name':'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Тетс на создание нового тега с неккоректными данными"""
        payload = {'name':''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        