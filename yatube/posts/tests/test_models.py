from django.contrib.auth import get_user_model
from django.test import TestCase
from groups.models import Group
from posts.models import Comment, Post
from pytils.translit import slugify

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.testuser = User.objects.create(username='testuser111')
        cls.group = Group.objects.create(title='Новая группа',
                                         slug=slugify('Новая группа'),
                                         description='Тестовая группа'
                                         )
        cls.post = Post.objects.create(
            text='Тестирование нового поста',
            author=cls.testuser,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.testuser,
            text='Это тестовый комментарий'
        )

    def test_attributes(self):
        """Проверка наличия атрибутов"""
        messages = {
            PostModelTest.post._meta.get_field('text').help_text:
            'Напишите содержание поста',
            PostModelTest.post._meta.get_field('text').verbose_name:
            'Текст поста',
            PostModelTest.post._meta.get_field('pub_date').verbose_name:
            'Дата публикации',
            PostModelTest.group._meta.get_field('title').help_text:
            'Напишите имя сообщества',
            PostModelTest.group._meta.get_field('title').verbose_name:
            'Наименование сообщества',
            PostModelTest.group._meta.get_field('slug').help_text:
            'Slug сообщества, заполняется автоматом',
            PostModelTest.group._meta.get_field('slug').verbose_name:
            'Slug сообщества',
            PostModelTest.group._meta.get_field('description').verbose_name:
            'Описание сообщества!',

        }
        for text, value in messages.items():
            with self.subTest(text=text):
                self.assertEqual(text, value)

    def test_string_respresntation(self):
        """Проверка преобразования"""
        strings = {
            str(PostModelTest.post): 'Тестирование но',
            str(PostModelTest.group): 'Новая группа',
            str(PostModelTest.comment): 'Это тестовый комментарий'[:15],
        }
        for model, represntation in strings.items():
            with self.subTest(model=model):
                self.assertEqual(model, represntation)
