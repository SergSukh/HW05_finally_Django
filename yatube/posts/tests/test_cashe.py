import shutil
import tempfile

from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import POSTS_IN_PAGE
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
        post_in_page = POSTS_IN_PAGE
        post = (Post(pk=i,
                     author=cls.user,
                     group=cls.group,
                     image=uploaded,
                     text=f'Тестовый текст{i}',
                     pub_date=datetime(2017, 1, i)
                     ) for i in range(1, post_in_page)
                )
        cls.post = Post.objects.bulk_create(post)


    def test_cashing_index_page(self):
        response = self.client.get('/')
        post = Post.objects.all()
        post_count = Post.objects.count()
        post.delete()
        """Проверили что посты в базе удалились"""
        self.assertNotEqual(len(response.context['page_obj']), Post.objects.count())
        """Проверили, что в кэше данные остались"""
        self.assertEqual(len(response.context['page_obj']), post_count)