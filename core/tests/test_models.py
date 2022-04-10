from django.test import TestCase, tag
from django.contrib.auth import get_user_model


from core import models

def sample_user(email = 'test@admin.com',  password='testpass'):

    return get_user_model().objects.create_user(email,password)

class ModelTest(TestCase):
    def test_create_user_widh_email_successfull(self):
        email = 'test@test.com'
        password = 'TestPasswod123'

        user = get_user_model().objects.create_user(
            email = email,
            password=password

        )
        self.assertEquals(user.email , email)
        self.assertTrue(user.check_password(password))


    def test_tag_str(self):
        """Тест на текстовое представление модели"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Рыба'
        )

        self.assertEqual(str(tag),tag.name)
        
    def test_ingredient_str(self):
            """Тест на текстовое представл"""
            ingredient = models.Ingredient.objects.create(
                user=sample_user(),
                name='Cucumber'
            )

            self.assertEqual(str(ingredient), ingredient.name)
    
    def test_recipe_str(self):
            """Тест на текстовое представл"""
            recipe = models.Recipe.objects.create(
                user=sample_user(),
                title='Steak and mushroom sauce',
                time_minutes=5,
                price=5.00
            )

            self.assertEqual(str(recipe), recipe.title)