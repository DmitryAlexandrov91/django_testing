
from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture()
def anonymous_client():
    return Client()


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def new():
    new = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return new


@pytest.fixture
def news_on_home_page():
    today = datetime.today()
    news = News.objects.bulk_create([
        News(title=f'Новость {index}',
             text='Текст новости.',
             date=today - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)])
    return news


@pytest.fixture
def comment(author, new):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария.'
    )
    return comment


@pytest.fixture
def comments_for_order_test(author, new):
    now = timezone.now()
    for index in range(10):
        comments = Comment.objects.create(
            news=new, author=author, text=f'Текст {index}'
        )
        comments.created = now + timedelta(days=index)
        comments.save()
    return comments


@pytest.fixture
def new_id_for_args(new):
    return (new.id,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Текст комментария.',
    }


@pytest.fixture
def form_data_for_edit():
    return {
        'text': 'Обновлённый комментарий',
    }


@pytest.fixture
def new_detail_url(new):
    url = reverse('news:detail', args=(new.id,))
    return url


@pytest.fixture
def comment_delete_url(comment):
    url = reverse('news:delete', args=(comment.id,))
    return url


@pytest.fixture
def comment_edit_url(comment):
    url = reverse('news:edit', args=(comment.id,))
    return url


@pytest.fixture
def url_to_comments(new_detail_url):
    return new_detail_url + '#comments'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
