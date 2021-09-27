from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание...'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста.',
            author=cls.author
        )

    def test_urls_correct_template(self):
        urls_to_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for adress, template in urls_to_template.items():
            with self.subTest(adress=adress):
                response = PostURLTests.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_redirect_for_guest(self):
        urls_redirect = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.id}
            ): (
                reverse('users:login') + '?next=' + reverse(
                    'posts:post_edit',
                    kwargs={'post_id': PostURLTests.post.id}
                )
            ),
            reverse('posts:post_create'): (
                reverse('users:login') + '?next=' + reverse(
                    'posts:post_create'
                )
            ),
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostURLTests.post.id}
            ): (
                reverse('users:login') + '?next=' + reverse(
                    'posts:add_comment',
                    kwargs={'post_id': PostURLTests.post.id}
                )
            )
        }
        for adress, redirect in urls_redirect.items():
            with self.subTest(adress=adress):
                response = PostURLTests.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_redirect_for_not_author(self):
        response = PostURLTests.user_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.id}
            )
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.id}
            )
        )

    def test_unexisting_page(self):
        response = PostURLTests.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
