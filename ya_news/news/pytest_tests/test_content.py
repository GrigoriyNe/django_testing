import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


HOME_URL = reverse('news:home')


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_count(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_contains_form(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url, data=form_data)
    form = response.context['form']
    assert 'form' in response.context
    assert type(form) == CommentForm


@pytest.mark.django_db
def test_detail_page_contains_form_not_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
@pytest.mark.usefixtures('all_comments')
def test_comments_order(client, comment, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
