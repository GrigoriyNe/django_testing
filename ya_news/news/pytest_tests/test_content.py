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
    dates_objects_list = [date for date in object_list]
    sorted_dates = sorted(
        object_list,
        key=lambda news: news.date,
        reverse=True
    )
    assert dates_objects_list == sorted_dates


@pytest.mark.django_db
def test_detail_page_contains_form(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url, data=form_data)
    response.context['form']
    isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_detail_page_doesnt_contain_form_for_anonymous(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_comments_order(client, all_comments, news):
    detail_url = reverse('news:detail', args=(news.id,))
    client.get(detail_url)
    comments = [comment for comment in all_comments]
    sorted_comments = sorted(
        all_comments,
        key=lambda comment: comment.created,
    )
    assert comments == sorted_comments
