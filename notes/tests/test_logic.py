# notes/tests/test_logic.py
from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotetCreation(TestCase):

    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании заметки.
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': 'zagolovok', 'slug': 'slug'}

    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом заметки.     
        self.client.post(self.url, data=self.form_data)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с заметками.
        # self.assertRedirects(response, f'{self.url}')
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть одна заметка.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        # self.assertEqual(note.text, self.NOTE_TEXT)
        # self.assertEqual(note.author, self.user)

    def test_not_unique_slug(self):
        # Создаём заметку в БД.
        note = Note.objects.create(title='Заголовок', text=self.NOTE_TEXT,  author=self.user, slug='slug')
        notes_count1 = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        notes_count2 = Note.objects.count()
        self.assertEqual(notes_count1, notes_count2)


    def test_slug_from_title(self):
        note = Note.objects.create(title=self.form_data['title'], text=self.NOTE_TEXT,  author=self.user, slug='')
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        assert new_note.slug == expected_slug  

class TestNoteEditDelete(TestCase):
    # Тексты для заметок не нужно дополнительно создавать 
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
    # поэтому их можно перечислить просто в атрибутах класса.
    NOTE_TEXT = 'Текст заметки!'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        
        # Создаём пользователя - автора заметки.
        cls.author = User.objects.create(username='Автор заметки')
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.author)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # URL для редактирования заметки.
        # Создаём заметку в БД.
        cls.note = Note.objects.create(title='Заголовок', text=cls.NOTE_TEXT, author=cls.author, slug='slug')
        # Формируем адрес блока с заметками, который понадобится для тестов.
        note_url = reverse('notes:detail', args=(cls.note.id,))  # Адрес заметки.
        cls.url_to_note = note_url  #  + '#comments'  # Адрес блока с заметками.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,)) 
        # URL для удаления комментария.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))  
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'text': cls.NEW_NOTE_TEXT, 'author': cls.author, 'title': 'Заголовок2', 'slug': 'slugslug'}  

    # def test_anonymous_user_cant_create_note(self):
    #     # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    #     # предварительно подготовленные данные формы с текстом комментария.
    #     # url = reverse('notes:add')     
    #     response = self.client.post(reverse('notes:add'), data=self.form_data)
    #     # Считаем количество комментариев.
    #     notes_count = Note.objects.count()
    #     # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    #     self.assertEqual(notes_count, 1)  # Одна заметка создана в setUpTestData

    # def test_user_can_create_note(self):
    #     # Совершаем запрос через авторизованный клиент.
    #     response = self.author_client.post(reverse('notes:add'), data=self.form_data)
    #     # Проверяем, что редирект привёл к разделу с комментами.
    #     # self.assertRedirects(response, f'{self.url}#comments')
    #     # Считаем количество комментариев.
    #     notes_count = Note.objects.count()
    #     # Убеждаемся, что есть один комментарий.
    #     self.assertEqual(notes_count, 2)
    #     # Получаем объект комментария из базы.
    #     # note = Note.objects.get()
    
    def test_author_can_delete_note(self):
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с заметками.
        # Заодно проверим статус-коды ответов.
        # self.assertRedirects(response, self.url_to_note)
        # # # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # # # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметка по-прежнему на месте.
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        # Выполняем запрос на редактирование от имени автора заметки.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        # self.assertRedirects(response, self.url_to_comments)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что текст заметки соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект заметки.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT) 

