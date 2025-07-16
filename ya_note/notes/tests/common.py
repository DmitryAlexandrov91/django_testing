from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class CommonCreateObjects(TestCase):
    NOTES_URL = reverse('notes:list')
    NOTES_FOR_TEST = 5

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Автор'
        )
        cls.another_user = User.objects.create(
            username='Другой пользователь'
        )
        Note.objects.bulk_create(
            [Note(
                title=f'заметка{index}',
                text='Текст заметки.',
                author=cls.author,
                slug=str(index)
            )
                for index in range(cls.NOTES_FOR_TEST)]
        )
        cls.another_user_note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки.',
            author=cls.another_user,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
