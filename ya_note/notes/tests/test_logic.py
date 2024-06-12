from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.form_data = {'text': cls.NOTE_TEXT}
        cls.author = User.objects.create(username='Автор заметки')

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_user_can_create_note(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=self.author
        )
        new_note = Note.objects.get()
        self.asseretequal_all_object_note(new_note)
        assert Note.objects.count() == 1

    def asseretequal_all_object_note(self, note):
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.login_url = reverse('users:login')
        self.expected_url = f'{self.login_url}?next={self.url}'
        assertRedirects(response, self.expected_url)
        assert Note.objects.count() == 0

    def test_not_unique_slug(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=self.author,
        )
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING),
        )
        assert Note.objects.count() == 1

    def test_automatic_creation_slug(self):
        self.client.post(self.url, data=self.form_data)
        self.note = Note.objects.create(
            title='Апандра',
            text='Текст заметки',
            author=self.author
        )
        note = Note.objects.get()
        self.assertEqual(note.slug, 'apandra')


class TestNoteEditDelite(TestCase):
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
        )
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': 'Текст', 'title': 'Заголовок'}

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        TestNoteCreation.asseretequal_all_object_note(self, self.note)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.success_url)
        count = Note.objects.count()
        self.assertEqual(count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        count = Note.objects.count()
        self.assertEqual(count, 1)
