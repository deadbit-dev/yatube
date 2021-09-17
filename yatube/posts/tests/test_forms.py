from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст поста.',
        }
        PostCreateFormTests.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count() - posts_count, 1)
        self.assertEqual(Post.objects.last().text, 'Тестовый текст поста.')

    def test_edit_post(self):
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=PostCreateFormTests.author,
        )
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст под изменениями.'}
        PostCreateFormTests.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.last().text, form_data['text'])
