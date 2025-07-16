from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.reader = User.objects.create(
            username='Другой пользователь'
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)

    def test_pages_for_all_users_availability(self):
        """Главная страница и страницы регистрации доступны
        всем пользователям.
        """
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        clients = self.client, self.user_client
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                for client in clients:
                    responce = client.get(url)
                    self.assertEqual(
                        responce.status_code,
                        HTTPStatus.OK,
                    )

    def test_pages_for_auth_user_availability(self):
        """Залогиненному юзеру доступны страницы заметок."""
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add')
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                responce = self.user_client.get(url)
                self.assertEqual(
                    responce.status_code,
                    HTTPStatus.OK,
                )

    def test_availability_for_note_edit_and_delete(self):
        """Страницы отдельной заметки, удаления и редактирования
        доступны только автору.
        """
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:delete', 'notes:edit'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    responce = self.client.get(url)
                    self.assertEqual(
                        responce.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект незалогинненого юзера."""
        login_url = reverse('users:login')
        slug = (self.note.slug,)
        not_for_guest_urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug),
        )
        for name, args in not_for_guest_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                responce = self.client.get(url)
                self.assertRedirects(responce, redirect_url)
