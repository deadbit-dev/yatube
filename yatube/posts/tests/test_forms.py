import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_post_form(self, post, form_data):
        self.assertEqual(
            post.author,
            PostCreateFormTests.author
        )
        self.assertEqual(
            post.text,
            form_data['text']
        )
        self.assertEqual(
            post.image,
            'posts/small.gif'
        ) if post.image else None

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст поста.',
            'image': PostCreateFormTests.image
        }
        posts_count = Post.objects.count()
        PostCreateFormTests.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.check_post_form(Post.objects.last(), form_data)

    def test_edit_post(self):
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=PostCreateFormTests.author,
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст под изменениями.',
        }
        PostCreateFormTests.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.check_post_form(Post.objects.last(), form_data)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='NoName')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_create_comment(self):
        post = Post.objects.create(
            text='Тестовый текст поста.',
            author=CommentFormTests.author
        )
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария.'
        }
        CommentFormTests.author_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comment = Comment.objects.last()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, CommentFormTests.author)
        self.assertEqual(comment.post, post)
