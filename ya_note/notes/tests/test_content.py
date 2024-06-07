from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Zagolovok',
            text='Текст',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_notes_list_for_author(self):
        url = self.LIST_URL
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        assert (self.note in object_list)

    def test_notes_list_for_not_author(self):
        url = self.LIST_URL
        self.client.force_login(self.reader)
        response = self.client.get(url)
        object_list = response.context['object_list']
        assert (self.note not in object_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(self.url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

                if self.client.force_login(self.reader):
                    response = self.client.get(self.url)
                    self.assertNotIn('form', response.context)
