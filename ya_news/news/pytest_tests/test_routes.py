import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('new_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_guests(client, name, args):
    """Анонимный пользователь имеет доступ к главной странице,
    странице отдельной новости и страницам регистрации.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, comment_id_for_args, expected_status
):
    """Доступ к редактированию и удалению комментариев есть только у автора."""
    url = reverse(name, args=comment_id_for_args)
    responce = parametrized_client.get(url)
    assert responce.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('new_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """Проверка переадресации анонимного юзера."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
