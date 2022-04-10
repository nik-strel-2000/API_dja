from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        """Предварительная подготовка для бидищих тестов"""
        #	В функцию setup выносится повторяющийся код из тестов, который предназначен для подготовки данных
        #	 для тестирования, т.е. тот код который будет запускаться каждый раз перед каждым тестом.
        #	В данном случае так как мы тестируем панель администратора мы будем инициализировать пользователя
        #	и авторизироваться в аккаунт
        #	https://dQcs.dianqoproiect.eom/en/2.2/topics/testinq/tools/#ovenview-and-a-quick-example
        #	Документация к модулю Client
        #	 В данном случае мы используем модуль Client для эмуляции пользователя
        self.client = Client() # Инициальзируем пользователя
        self.admin_user = get_user_model().objects.create_superuser( # Создаем админскую учетную запись
            email='admin@admin.com', 
            password='Someadminpasswprd77'
        )
        self.client.force_login(self.admin_user) #Авторизируемся
        self.user = get_user_model().objects.create_user( 
            #Создаем обыного пользователя
            email = 'user@test.com',
            password = 'passwordUser1',
            name= 'Test user full name'
        )

    def test_users_listed(self):
        """Тест на создание списка пользователей"""
        url = reverse('admin:core_user_changelist') #Генерируем с помощью фунуции reverse url для списка пользователей 
        res = self.client.get(url) # Получаем содержимое get запроса по данному адресу
        self.assertContains(res, self.user.name) # Проверяем наличие имени и почты пользователя в содержимом
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Тест страницы редактирования аккацнта пользователя"""

        url = reverse('admin:core_user_change', args=[self.user.id])
        # /admin/core/user/1
        res = self.client.get(url) 

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Проверка страницы создания пользователя"""

        url = reverse('admin:core_user_add')
        res= self.client.get(url)

        self.assertEqual(res.status_code, 200)

