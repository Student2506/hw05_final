from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post
from groups.models import Group
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

    def test_attributes(self):
        """Проверка наличия атрибутов"""
        messages = {
            self.post._meta.get_field('text').help_text:
            'Напишите содержание поста',
            self.post._meta.get_field('text').verbose_name:
            'Текст поста',
            self.post._meta.get_field('pub_date').verbose_name:
            'Дата публикации',
            self.group._meta.get_field('title').help_text:
            'Напишите имя сообщества',
            self.group._meta.get_field('title').verbose_name:
            'Наименование сообщества',
            self.group._meta.get_field('slug').help_text:
            'Slug сообщества, заполняется автоматом',
            self.group._meta.get_field('slug').verbose_name:
            'Slug сообщества',
            self.group._meta.get_field('description').verbose_name:
            'Описание сообщества!',

        }
        for text, value in messages.items():
            with self.subTest(text=text):
                self.assertEqual(text, value)

    def test_string_respresntation(self):
        """Проверка преобразования"""
        strings = {
            str(self.post): 'Тестирование но',
            str(self.group): 'Новая группа',
        }
        for model, represntation in strings.items():
            with self.subTest(model=model):
                self.assertEqual(model, represntation)
