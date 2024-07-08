# news/tests/test_content.py
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
from django.utils import timezone

from notes.models import Note
# Импортируем класс формы.
from notes.forms import NoteForm

User = get_user_model()

class TestHomePage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    HOME_URL = reverse('notes:list')
    # EDIT_URL = reverse('notes:edit')
    # DELETE_URL = reverse('notes:delete')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.other = User.objects.create(username='another_user')
        cls.note_author = Note.objects.create(title='ЗаголовокX', text='Текст', author=cls.author, slug='slug')
        cls.note_other = Note.objects.create(title='ЗаголовокY', text='Текст', author=cls.other, slug='slug2')
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))
        cls.add_url = reverse('notes:add')

    def test_note_in_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author, object_list)

    def test_note_in_author_not_in_other_context(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list_author = response.context['object_list']
        self.client.force_login(self.other)
        response = self.client.get(self.HOME_URL)
        object_list_other = response.context['object_list']
        self.assertNotIn(object_list_author, object_list_other)
        self.assertNotIn(object_list_other, object_list_author)

    
    def test_authorized_client_has_edit_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm) 

    def test_authorized_client_has_add_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm) 

