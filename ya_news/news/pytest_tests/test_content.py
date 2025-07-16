import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, news_on_home_page):
    """Проверка отображения корректного количества новостей на главной."""
    url = reverse('news:home')
    responce = client.get(url)
    object_list = responce.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_on_home_page):
    """Проверка сортировки новостей на главной странице."""
    url = reverse('news:home')
    responce = client.get(url)
    object_list = responce.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, new, comments_for_order_test):
    """Проверка сортировки комментариев."""
    detail_url = reverse('news:detail', args=(new.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [
        comments_for_order_test.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('anonymous_client'), False),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_pages_contains_form(parametrized_client, name, args, form_on_page):
    """Проверка наличия формы на страницах."""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) == form_on_page
    if 'form' in response.context:
        assert isinstance(response.context['form'], CommentForm)
