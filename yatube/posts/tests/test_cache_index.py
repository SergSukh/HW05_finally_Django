import shutil
import tempfile

from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post
from .fixtures import constant_post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title=constant_post.test_group['title'],
            slug=constant_post.test_group['slug'],
            description=constant_post.test_group['description'],
        )
        post_in_page = settings.POSTS_IN_PAGE
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post = (Post(pk=i,
                     author=cls.user,
                     group=cls.group,
                     image=uploaded,
                     text=f'Тестовый текст{i}',
                     pub_date=datetime(2017, 1, i)
                     ) for i in range(1, post_in_page)
                )
        cls.post = Post.objects.bulk_create(post)
        cls.url = '/'
        cls.page = ('posts:index')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_cache_index_create_post(self):
        cache.clear()
        self.client.get(reverse(self.page))
        form_data = {
            'text': 'Тест для КЭШ',
            'group': f'{self.group.pk}',
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_case = Post.objects.first()
        """Проверили, что поста на странице нет"""
        response_1 = self.client.get(reverse(self.page))
        self.assertNotIn(post_case.text, response_1.content.decode())
        """Проверили, в кэше данные остались"""
        cache.clear()
        response_2 = self.client.get(reverse(self.page))
        self.assertIn(post_case, response_2.context.get('page_obj'))
