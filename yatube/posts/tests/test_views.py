import shutil
import tempfile
import time

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from pytils.translit import slugify
from django.core.cache import cache


from posts.models import Post
from groups.models import Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(username='PavelZ')

        cls.group = Group.objects.create(
            title='Новая группа',
            slug=slugify('Новая группа'),
            description='Новая группа описание'
        )
        cls.post = Post.objects.create(
            text='Тестирование нового поста111',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.group_other = Group.objects.create(
            title='Другая группа',
            slug=slugify('Другая группа'),
            description='Другая группа описание'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_doesnt_appear_on_other_group(self):
        """Проверка, что пост не появляется в пространстве 'Другая группа'"""
        response = self.authorized_client.get(
            reverse('slug', kwargs={'slug': slugify('Другая группа')})
        )
        if(len(response.context.get('page').object_list) > 0):
            self.assertNotEqual(
                response.context.get('page').object_list[0].text,
                'Тестирование нового поста111'
            )

    def test_view_uses_correct_template(self):
        """Проверка, что views используют корректные шаблоны."""
        templates_view = {
            reverse('index'): 'index.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('slug', kwargs={'slug': slugify('Новая группа')}):
                'group.html',
            reverse('profile', kwargs={'username': self.user.username}):
                'profile.html',
            reverse('post', kwargs={'username': self.user.username,
                    'post_id': self.post.pk}): 'post.html',
            reverse('post_edit', kwargs={'username': self.user.username,
                    'post_id': self.post.pk}): 'new_edit_post.html',
            reverse('new_post'): 'new_edit_post.html'
        }
        for url, template in templates_view.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_appears_on_appropriate_pages(self):
        """Проверка, что пост отображется на главной и в сообществе"""
        pages_to_check = {
            'index': reverse('index'),
            'slug': reverse('slug', kwargs={'slug': slugify('Новая группа')}),
            'profile': reverse('profile',
                               kwargs={'username': self.user.username}),
            'post': reverse('post', kwargs={'username': self.user.username,
                                            'post_id': self.post.id})
        }
        for url, url_reverse in pages_to_check.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url_reverse)
                if url == 'post':
                    first_object = response.context['post']
                else:
                    first_object = response.context['page'][0]
                task_text_0 = first_object.text
                task_image_0 = first_object.image
                self.assertEqual(task_text_0, 'Тестирование нового поста111')
                self.assertIsInstance(task_image_0, ImageFieldFile)
                self.assertTrue('small.gif' in task_image_0.path)

    def test_pages_contain_according_records(self):
        """Проверка, что страница показывает не более 10 постов"""
        for i in range(12):
            Post.objects.create(
                text='Тестирование нового поста111' + str(i),
                author=self.user
            )
        per_pages = [10, 3]

        for page, qty in enumerate(per_pages, 1):
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse('index'), {'page': page}
                )
                self.assertEqual(
                    len(response.context.get('page').object_list), qty
                )

    def test_post_filling_form_shows_correct_context(self):
        """Шаблон создания/редактирования сформирован с правльным контекстом"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        form_pages = {
            reverse('new_post'): form_fields,
            reverse('post_edit', kwargs={'username': self.user.username,
                    'post_id': self.post.pk}): form_fields
        }
        for url, fields in form_pages.items():
            response = self.authorized_client.get(url)
            for value, expected in fields.items():
                with self.subTest(url=url, value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_caching(self):
        """Проверка, что кэш есть"""
        for i in range(12):
            Post.objects.create(
                text='Тестирование нового поста111' + str(i),
                author=self.user
            )
            last_post = 'Тестирование нового поста111' + str(i)

        pages_to_check = {
            'index': reverse('index'),
        }
        for url, url_reverse in pages_to_check.items():
            with self.subTest(url=url, url_reverse=url_reverse):
                cache.clear()
                cache.set('foo', 'bar', 10)
                var = cache.get('foo')
                self.assertEqual(var, 'bar')
                time.sleep(11)
                var2 = cache.get('foo')
                self.assertIsNone(var2)
                response = self.authorized_client.get(url_reverse)
                self.assertTrue(last_post.encode() in response.content)
                caching_test = 'Кэш в действии'
                Post.objects.create(
                    text=caching_test,
                    author=self.user
                )
                response = self.authorized_client.get(url_reverse)
                self.assertFalse(caching_test.encode() in response.content)
