from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post, Group
from http import HTTPStatus
from pytils.translit import slugify

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='PavelZ')
        cls.other_user = User.objects.create(username='SomeUser')

        cls.group = Group.objects.create(title='Новая группа',
                                         slug=slugify('Новая группа'),
                                         description='Тестовая группа'
                                         )
        cls.post = Post.objects.create(
            text='Тестирование нового поста',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(self.other_user)

    def test_post_edit_url_redirect_non_owner(self):
        """Страница /<profile>/<post-id>/edit/ корректно перенаправляет
        'неавтора'.
        """
        response = self.other_authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username,
                    'post_id': self.post.pk}
        ),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id})
        )

    def test_public_urls_at_desired_locations(self):
        """Проверка работоспособности общедоступных URL."""
        anon_users_url = {
            'index': {},
            'about:author': {},
            'about:tech': {},
            'slug': {'slug': slugify('Новая группа')},
            'profile': {'username': self.user.username},
            'post': {'username': self.user.username, 'post_id': self.post.pk}
        }

        for url_reverse, kwargs in anon_users_url.items():
            with self.subTest(url_reverse=url_reverse):
                response = self.guest_client.get(
                    reverse(url_reverse, kwargs=kwargs)
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.authorized_client.get(
                    reverse(url_reverse, kwargs=kwargs)
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_restricted_urls_at_desired_locations(self):
        """Проверка работоспособности URL для "залогиненнных"."""
        authorized_users_url = {
            'post_edit': {
                'username': self.user.username, 'post_id': self.post.pk
            },
            'new_post': {}
        }

        for url_reverse, kwargs in authorized_users_url.items():
            with self.subTest(url_reverse=url_reverse):
                response = self.guest_client.get(
                    reverse(url_reverse, kwargs=kwargs),
                    follow=True
                )
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={reverse(url_reverse, kwargs=kwargs)}'
                )
            with self.subTest(url_reverse=url_reverse):
                response = self.authorized_client.get(
                    reverse(url_reverse, kwargs=kwargs),
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """Проверка использования шаблона"""
        url_template_list = {
            reverse('index'): 'index.html',
            reverse('profile',
                    kwargs={'username': self.user.username}): 'profile.html',
            reverse('post',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.pk}): 'post.html',
            reverse('post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.pk}): 'new_edit_post.html',
            reverse('slug', kwargs={'slug': self.group.slug}): 'group.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        for url_reverse, template in url_template_list.items():
            with self.subTest(url_reverse=url_reverse):
                response = self.authorized_client.get(url_reverse)
                self.assertTemplateUsed(response, template)

    def test_error_code_if_page_not_found(self):
        """Проверка, что сервер возвращает код 404, если страница не найдена"""
        url_template_list = {
            '/index123/': HTTPStatus.NOT_FOUND,
            reverse('slug', kwargs={'slug': 'not_a_real_slug'}):
                HTTPStatus.NOT_FOUND
        }

        for url_reverse, error_code in url_template_list.items():
            with self.subTest(url_reverse=url_reverse, error_code=error_code):
                response = self.guest_client.get(url_reverse)
                self.assertEqual(response.status_code, error_code)
