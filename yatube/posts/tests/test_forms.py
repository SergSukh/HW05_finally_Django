import shutil
import tempfile

from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post, Comment
from .fixtures.constant_post import test_post_text, test_group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_guest_create_post(self):
        """Валидная форма создает запись в Post."""
        login_url = reverse('users:login')
        create_url = reverse('posts:post_create')
        response = self.guest.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый текст2',
                'group': f'{self.group.pk}',
            },
            follow=True
        )
        self.assertRedirects(
            response, f'{login_url}?next={create_url}',
            302, 200, fetch_redirect_response=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст2',
            'group': f'{self.group.pk}',
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.order_by('pub_date').last()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)

    def test_edit_post(self):
        self.auth_client.force_login(self.user)
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тeкстовый тeст',
            'group': f'{self.group.pk}',
        }
        post_old = get_object_or_404(Post, pk=self.post.pk)
        response = self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': (self.post.pk)}),
            data=form_data,
            follow=True
        )
        post = get_object_or_404(Post, pk=self.post.pk)
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(post_count, self.post.pk)
        self.assertEqual(post.group, self.post.group)
        self.assertNotEqual(post.text, post_old.text)

    def test_creat_post_image_content(self):
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст3',
            'group': f'{self.group.pk}',
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст3',
                author=self.user,
                group=self.group.pk,
                # image='posts/small.gif'
            ).exists()
        )
    
    def test_add_comment_auth_user(self):
        """Валидная форма создает запись в Comment."""
        comment_count = Comment.objects.count()
        post = Post.objects.first()
        form = {
            'text': 'Тестовый комментарий2',
            'post_id': f'{post.pk}',
        }
        response = self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': f'{post.pk}'}),
            data=form,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        new_comment = Comment.objects.first()
        self.assertEqual(new_comment.text, form['text'])
        self.assertEqual(new_comment.author, self.user)

    def test_guest_not_add_comment(self):
        post = Post.objects.first()
        login_url = reverse('users:login')
        create_url = reverse('posts:add_comment',
                             kwargs={'post_id': f'{post.pk}',})
        response = self.guest.post(
            reverse('posts:add_comment', kwargs={'post_id': f'{post.pk}'}),
            data={
            'text': 'Тестовый комментарий2',
            'post_id': f'{post.pk}',},
            follow=True
        )
        self.assertRedirects(response, f'{login_url}?next={create_url}',
            302, 200, fetch_redirect_response=True)
