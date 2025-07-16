from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.utils import comment_counter


def test_anonymous_user_cant_create_comment(
        client, form_data, new_detail_url):
    """Анонимный пользователь не может оставить комментарий."""
    comments_before_changes = comment_counter()
    client.post(new_detail_url, data=form_data)
    assert comment_counter() == comments_before_changes


def test_auth_user_can_create_comment(
        author_client, form_data, new_detail_url):
    """Авторизованный пользователь может оставить комментарий."""
    comments_before_changes = comment_counter()
    author_client.post(new_detail_url, data=form_data)
    assert comment_counter() == comments_before_changes + 1
    created_comment = Comment.objects.get()
    assert created_comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client, new_detail_url):
    """Комментарий не содержит запрещённые слова."""
    comments_before_changes = comment_counter()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(new_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comment_counter() == comments_before_changes


def test_author_can_delete_comment(
        author_client, comment_delete_url, url_to_comments):
    """Пользователь может удалить свой комментарий."""
    comments_before_changes = comment_counter()
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert comment_counter() == comments_before_changes - 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_delete_url):
    """Пользователь не может удалить чужой комментарий."""
    comments_before_changes = comment_counter()
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment_counter() == comments_before_changes


def test_author_can_edit_comment(
        author,
        author_client,
        comment_edit_url,
        form_data_for_edit,
        url_to_comments):
    """Пользователь может отредактировать свой комментарий."""
    response = author_client.post(
        comment_edit_url, data=form_data_for_edit)
    assertRedirects(response, url_to_comments)
    changed_comment = Comment.objects.get(pk=author.id)
    assert changed_comment.text == form_data_for_edit['text']


def test_user_cant_edit_comment_of_another_user(
        author,
        not_author_client,
        comment_edit_url,
        form_data,
        form_data_for_edit):
    """Пользователь не может отредактировать чужой комментарий."""
    response = not_author_client.post(
        comment_edit_url, data=form_data_for_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    changed_comment = Comment.objects.get(pk=author.id)
    assert changed_comment.text == form_data['text']
