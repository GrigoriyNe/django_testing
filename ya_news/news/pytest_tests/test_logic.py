from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, news_id_for_args
    ):
    form_data = {'text': COMMENT_TEXT}
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    comments_count = Comment.objects.count()
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert (comments_count == 0)


def test_user_cant_use_bad_words(
        author_client, news_id_for_args
        ):
    url = reverse('news:detail', args=news_id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert (Comment.objects.count() == comments_count)
    assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )


def test_user_can_create_comment(
        author_client, author, news, news_id_for_args
        ):
    form_data = {'text': COMMENT_TEXT}
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert (comments_count == 1)
    comment = Comment.objects.get()
    assert (comment.text == COMMENT_TEXT)
    assert (comment.news == news)
    assert (comment.author == author)


def test_author_can_delete_comment(author_client, id_for_args, news_id_for_args):
    comments_count = Comment.objects.count()
    delete_url = reverse('news:delete', args=id_for_args)
    url = reverse('news:detail', args=news_id_for_args)
    url_to_comments = url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client, id_for_args
        ):
    comments_count = Comment.objects.count()
    delete_url = reverse('news:delete', args=id_for_args)
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(author_client, comment, news):
    form_data = {'text': NEW_COMMENT_TEXT}
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert(comment.text == NEW_COMMENT_TEXT)


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}
    response = not_author_client.post(edit_url, data=form_data)
    assert (response.status_code == HTTPStatus.NOT_FOUND)
    comment.refresh_from_db()
    assert(comment.text == COMMENT_TEXT) 
