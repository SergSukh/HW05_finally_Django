from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post
from .fixtures.constant_post import test_post_text, test_group

User = get_user_model()


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

    def setUp(self):
        self.guest = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_guest_create_post(self):
        """Валидная форма создает запись в Post."""
        login_url = reverse('users:login')
        create_url = reverse('posts:post_create')
        responce = self.guest.post(
            reverse('posts:post_create'),
            data={
                'text': 'Тестовый текст2',
                'group': f'{self.group.pk}',
            },
            follow=True
        )
        self.assertRedirects(
            responce, f'{login_url}?next={create_url}',
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
        new_post = Post.objects.first()
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_count, self.post.pk)
        self.assertEqual(post.group, self.post.group)
        self.assertNotEqual(post.text, post_old.text)
