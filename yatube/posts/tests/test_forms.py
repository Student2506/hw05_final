import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from pytils.translit import slugify

from groups.models import Group
from posts.models import Post, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='PavelZ')
        cls.testgroup = Group.objects.create(
            title='Тестовая группа',
            slug=slugify('Тестовая группа'),
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Новый тестовый пост',
            author=cls.user,
            group=cls.testgroup
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        return super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Тестирование формы создания поста"""
        posts_count = Post.objects.count()
        group_pk = PostCreateFormTests.testgroup.pk
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
        form_data = {
            'text': 'Новый тестовый пост',
            'group': group_pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        new_post_object = Post.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(
            Post.objects.count(), posts_count + 1
        )
        self.assertEqual(new_post_object.text, 'Новый тестовый пост')
        self.assertEqual(new_post_object.group.title, 'Тестовая группа')
        self.assertEqual(new_post_object.author.username, 'PavelZ')

    def test_edit_post(self):
        """Тестирование формы редактирования поста"""
        posts_count = Post.objects.count()
        group_new = Group.objects.create(
            title='Вторая Тестовая группа',
            slug=slugify('Вторая Тестовая группа'),
            description='Вторая положительная группа'
        )

        post_pk = PostCreateFormTests.post.pk
        form_data = {
            'text': 'Новый тестовый пост123456',
            'group': group_new.pk
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': PostCreateFormTests.user.username,
                'post_id': post_pk
            }),
            data=form_data,
            follow=True
        )

        edited_post_object = Post.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('post', kwargs={
            'username': PostCreateFormTests.user.username,
            'post_id': post_pk
        }))
        self.assertEqual(edited_post_object.text, 'Новый тестовый пост123456')
        self.assertEqual(
            edited_post_object.group.title,
            'Вторая Тестовая группа'
        )
        self.assertEqual(edited_post_object.author.username, 'PavelZ')
        self.assertEqual(
            Post.objects.count(), posts_count
        )

    def test_comments_form(self):
        """Тестирование создания комментариев."""
        form_data = {
            'text': 'Новый комментарий'
        }
        response = self.authorized_client.post(
            reverse('add_comment',
                    kwargs={
                        'username': PostCreateFormTests.user.username,
                        'post_id': PostCreateFormTests.post.id
                    }),
            data=form_data,
            follow=True
        )
        last_comment = PostCreateFormTests.post.comments.last()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': PostCreateFormTests.user.username,
                'post_id': PostCreateFormTests.post.id
            }
        ))
        self.assertEqual(last_comment.text, 'Новый комментарий')
        self.assertEqual(last_comment.author, PostCreateFormTests.user)
