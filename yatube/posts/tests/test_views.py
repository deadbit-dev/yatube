import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from django.urls import reverse
from django import forms

from ..models import Post, Group, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.count_posts_on_page = 10
        cls.count_posts = 15
        cls.rest_posts = cls.count_posts % cls.count_posts_on_page
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание...'
        )
        posts = (
            Post(
                text='Тестовый текст поста.',
                author=cls.user,
                group=cls.group
            ) for i in range(cls.count_posts)
        )
        Post.objects.bulk_create(posts, cls.count_posts)

    def test_paginator_pages(self):
        pages_paginator = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorTest.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorTest.user}
            )
        ]
        for page in pages_paginator:
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
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorTest.rest_posts
                )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание...'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста.',
            image=image,
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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

    def check_post_context(self, post):
        self.assertEqual(post.id, PostPagesTests.post.id)
        self.assertEqual(post.author, PostPagesTests.post.author)
        self.assertEqual(post.text, PostPagesTests.post.text)
        self.assertEqual(post.image, PostPagesTests.post.image)
        self.assertEqual(post.group, PostPagesTests.post.group)

    def test_index_page_context(self):
        response = PostPagesTests.user_client.get(reverse('posts:index'))
        self.check_post_context(response.context['page_obj'][0])

    def test_group_list_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        self.check_post_context(response.context['page_obj'][0])
        self.assertEqual(
            PostPagesTests.group,
            response.context['group']
        )

    def test_new_group_list_none(self):
        group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug-new',
            description='Описание...'
        )
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': group.slug}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user}
            )
        )
        self.check_post_context(response.context['page_obj'][0])
        self.assertEqual(
            PostPagesTests.user,
            response.context['author']
        )
        self.assertIsNotNone(response.context['following'])

    def test_post_detail_page_context(self):
        response = PostPagesTests.user_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.id}
            )
        )
        self.check_post_context(response.context['post'])
        form_fields = {'text': forms.fields.CharField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields.get(value)
                self.assertIsInstance(form_fields, expected)
        self.assertIsNotNone(response.context['comments'])

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

    def test_cache_index(self):
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=PostPagesTests.user,
        )
        response = PostPagesTests.user_client.get(
            reverse('posts:index')
        )
        page = response.content
        post.delete()
        response = PostPagesTests.user_client.get(
            reverse('posts:index')
        )
        self.assertEqual(page, response.content)
        cache.clear()
        response = PostPagesTests.user_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(page, response.content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_following_auth(self):
        FollowTests.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        follow = Follow.objects.last()
        self.assertEqual(follow.user, FollowTests.user)
        self.assertEqual(follow.author, FollowTests.author)

    def test_unfollow_auth(self):
        FollowTests.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        follows_count = Follow.objects.count()
        FollowTests.user_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follows_count - 1)

    def test_new_post_follow(self):
        FollowTests.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=FollowTests.author,
        )
        response = FollowTests.user_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertEqual(
            post.id, response.context['page_obj'][0].id
        )

    def test_new_post_unfollow(self):
        FollowTests.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.author}
            )
        )
        Post.objects.create(
            text='Тестовый текст поста.',
            author=FollowTests.author,
        )
        user = User.objects.create_user(username='NameNo')
        user_client = Client()
        user_client.force_login(user)
        response = user_client.get(
            reverse(
                'posts:follow_index'
            )
        )
        self.assertEqual(len(response.context['page_obj']), 0)
