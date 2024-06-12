import pytest

from django.conf import settings
from django.urls import reverse

from http import HTTPStatus

from news.forms import CommentForm


HOME_URL = reverse('news:home')


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
def test_news_count(client):
    response = client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK
    news_on_home_page = response.context['object_list']
    news_count = news_on_home_page.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(HOME_URL)
    assert response.status_code == HTTPStatus.OK
    news_on_home_page = response.context['object_list']
    sorted_news = sorted(
        news_on_home_page,
        key=lambda news: news.date,
        reverse=True
    )
    assert list(news_on_home_page) == sorted_news


@pytest.mark.django_db
def test_detail_page_contains_form(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
    isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_detail_page_doesnt_contain_form_for_anonymous(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comments_order(client, all_comments, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK
    sorted_comments = sorted(
        all_comments,
        key=lambda comment: comment.created,
    )
    assert list(all_comments) == sorted_comments
