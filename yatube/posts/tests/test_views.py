from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.count_posts_on_page = 10
        cls.count_posts = 15
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание...'
        )
        cls.posts = (
            Post(
                text='Тестовый текст поста.',
                author=cls.user,
                group=cls.group if i <= cls.count_posts_on_page else None
            ) for i in range(cls.count_posts)
        )
        Post.objects.bulk_create(cls.posts, cls.count_posts)

    def test_paginator_pages(self):
        pages_paginator = {
            reverse(
                'posts:index'
            ): PaginatorTest.count_posts % PaginatorTest.count_posts_on_page,
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorTest.group.slug}
            ): 1,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorTest.user}
            ): PaginatorTest.count_posts % PaginatorTest.count_posts_on_page
        }
        for page, total in pages_paginator.items():
            with self.subTest(page=page):
                response = PaginatorTest.user_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), (
                        PaginatorTest.count_posts_on_page
                    )
                )
                response = PaginatorTest.user_client.get(
                    page + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), total)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание...'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста.',
            author=cls.user,
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostPagesTests.user_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        response = PostPagesTests.user_client.get(reverse('posts:index'))
        self.assertIsNotNone(response.context['page_obj'])

    def test_group_list_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        self.assertIsNotNone(response.context['page_obj'])
        self.assertIsNotNone(response.context['group'])

    def test_profile_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user}
            )
        )
        self.assertIsNotNone(response.context['page_obj'])
        self.assertIsNotNone(response.context['author'])

    def test_post_detail_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        self.assertIsNotNone(response.context['post'])

    def test_edit_post_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        self.assertIsNotNone(response.context['form'])
        self.assertIsNotNone(response.context['is_edit'])
        self.assertTrue(response.context['is_edit'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_create_post_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_have_post_on_pages(self):
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=PostPagesTests.user,
            group=PostPagesTests.group
        )
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user}
            )
        ]
        for page in pages:
            with self.subTest(page=page):
                response = PostPagesTests.user_client.get(page)
                self.assertTrue(
                    post in response.context['page_obj'].object_list
                )
