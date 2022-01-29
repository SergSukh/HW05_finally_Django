from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Post, Group
from .fixtures.constant_post import test_post_text, test_group

User = get_user_model()


class StaticURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages(self):
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            response = self.guest_client.get(url)
            self.assertNotEqual(
                response.status_code,
                404,
                f'страница {url} не найдена проверьте URL_PATH')
            self.assertEqual(
                response.status_code,
                200,
                (f'Ошибка {response.status_code} при открытиии `{url}`.',
                 ' Проверьте ее view-функцию'))


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title=test_group['title'],
            slug=test_group['slug'],
            description=test_group['description'],
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=test_post_text,
            group=cls.group,
        )
        # Список URL адресов и шаблонов для тестирования:

        cls.url_name_user_close = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }

        cls.url_name_guest = {
            '/': 'posts/index.html',
            f'/group/{cls.post.group}/': 'posts/group_list.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/profile/{cls.post.author}/': 'posts/profile.html',
        }

        cls.url_name_guest_close = {
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        users = ['author', 'HasNoName', 'Guest']
        for user in users:
            if user == 'author':
                templates_url_names = self.url_name_user_close.copy()
                templates_url_names.update(self.url_name_guest_close)
                templates_url_names.update(self.url_name_guest)
                closed_url_names = {}
            elif user == 'HasNoName':
                self.user = User.objects.create_user(username='HasNoName')
                self.client = Client()
                self.client.force_login(self.user)
                templates_url_names = {}
                templates_url_names = self.url_name_guest.copy()
                templates_url_names.update(self.url_name_guest_close)
                closed_url_names = self.url_name_user_close
            else:
                self.client = Client(user)
                templates_url_names = self.url_name_guest
                closed_url_names = self.url_name_guest_close.copy()
                closed_url_names.update(self.url_name_user_close)
            for address, template in templates_url_names.items():
                with self.subTest(address=address):
                    response = self.client.get(address)
                    self.assertNotEqual(response.status_code, 404)
                    self.assertTemplateUsed(response, template)
            for address, template in closed_url_names.items():
                with self.subTest(address=address):
                    response = self.client.get(address)
                    self.assertNotEqual(response.status_code, 404)
                    self.assertEqual(response.status_code, 302)
