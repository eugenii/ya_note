from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаём тестовую заметку
        cls.note = Note.objects.create(title='Заголовок', text='Текст', author=cls.author, slug='slug')
        # От имени одного пользователя создаём комментарий к новости:
        # cls.comment = Comment.objects.create(
        #     news=cls.news,
        #     author=cls.author,
        #     text='Текст комментария'
        # ) 

    def test_pages_availability(self):
        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = (
            # Путь для главной страницы не принимает
            # никаких позиционных аргументов, 
            # поэтому вторым параметром ставим None.
            ('notes:home', None),
            # Путь для страницы новости 
            # принимает в качестве позиционного аргумента
            # id записи; передаём его в кортеже.
            # ('notes:detail', (self.note.slug,)),  # перенесём в другой тест - туда где авторизованный пользователь что-то делает..
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        # Итерируемся по внешнему кортежу 
        # и распаковываем содержимое вложенных кортежей:
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_autors_pages_and_actions(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),  # авторизованный должен получить ответ OK,
            (self.reader, HTTPStatus.NOT_FOUND),  # неавторизованный должен получить ответ NOT_FOUND.
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            urls = (
                ('notes:add', None),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
                ('notes:detail', (self.note.slug,)),
                ('notes:list', None),
                ('notes:success', None),
            )
            for name, args in urls:  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.note.slug,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)

