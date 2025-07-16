
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.common import CommonCreateObjects


class TestNotesList(CommonCreateObjects):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author_response = cls.author_client.get(cls.NOTES_URL)
        cls.object_list = cls.author_response.context['object_list']
        # cls.another_user_response = cls.author_client.get(cls.NOTES_URL)

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        response = self.another_user_client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        # object_list = self.another_user_response.context['object_list']
        self.assertIn(self.another_user_note, object_list)

    def test_only_author_notes(self):
        """Проверка на отображение только заметок автора."""
        author_notes_list = Note.objects.filter(
            author_id=self.author.id
        )
        self.assertQuerysetEqual(
            author_notes_list, self.object_list, ordered=False)

    def test_news_order(self):
        """Сортировка заметок на странице по ID."""
        author_notes = [note.id for note in self.object_list]
        sorted_dates = sorted(author_notes)
        self.assertEqual(author_notes, sorted_dates)

    def test_authorized_client_has_create_note_form(self):
        """Проверка наличия формы на странице создания заметки."""
        response = self.author_client.get(
            reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_note_form(self):
        """Проверка наличия формы на странице редактирования заметки."""
        response = self.another_user_client.get(
            reverse('notes:edit',
                    kwargs={'slug': self.another_user_note.slug}))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
