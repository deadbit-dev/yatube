from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст тестового поста.',
        )

    def test_post_have_correct_object_names(self):
        post = PostModelTest.post
        post_str = str(post)
        self.assertEqual(post_str, post.text[:15])

    def test_post_have_correct_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_have_correct_help_text(self):
        post = PostModelTest.post
        field_help = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_have_correct_object_names(self):
        group = GroupModelTest.group
        group_str = str(group)
        self.assertEqual(group_str, group.title)

    def test_group_have_correct_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Адрес для страницы с группой',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )
