from datetime import datetime
from urllib import response

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.conf import settings
from django.urls import reverse

from posts.models import Group, Post, Follow
from yatube.settings import POSTS_IN_PAGE
from .fixtures import constant_post


User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='follower')
        cls.user_2 = User.objects.create_user(username='not_follower')
        cls.group = Group.objects.create(
            title=constant_post.test_group['title'],
            slug=constant_post.test_group['slug'],
            description=constant_post.test_group['description'],
        )
        post_in_page = settings.POSTS_IN_PAGE
        post = (Post(pk=i,
                     author=cls.author,
                     group=cls.group,
                     text=f'Тестовый текст{i}',
                     pub_date=datetime(2017, 1, i)
                     ) for i in range(1, post_in_page * 2)
                )
        cls.post = Post.objects.bulk_create(post)

    def setUp(self):
        self.guest = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.auth_client_2 = Client()
        self.auth_client_2.force_login(self.user_2)

    def test_guest_not_follow(self):
        """Неавторизованный пользователь не может подписываться"""
        login_url = reverse('users:login')
        create_url = reverse(f'posts:profile_follow', kwargs={'username': f'{self.author}'})
        response = self.guest.get(create_url)
        self.assertRedirects(response, f'{login_url}?next={create_url}', 302, 200)

    def test_user_follow_unfollow_other(self):
        create_url = reverse(f'posts:profile_follow', kwargs={'username': self.author.username,})
        delete_url = reverse(f'posts:profile_unfollow', kwargs={'username': self.author.username,})
        author_follow_count = self.author.following.count()
        user_follow_count = self.user.follower.count()
        """Создаем подписку и проверяем появление ее у автора и пользователя"""
        self.auth_client.get(create_url)
        author_follow_count_new = self.author.following.count()
        user_follow_count_new = self.user.follower.count()
        """Проверили, что подписки у автора и пользователя поменялись одинаково"""
        self.assertEqual((author_follow_count_new - author_follow_count), (user_follow_count_new - user_follow_count))
        """А тут проверили, что кол-во подписок увеличилось именно на 1"""
        self.assertEqual(user_follow_count_new, user_follow_count + 1)
        """Теперь так же проверим, что пользователь может отписаться"""
        self.auth_client.get(delete_url)
        author_follow_count_new = self.author.following.count()
        user_follow_count_new = self.user.follower.count()
        self.assertEqual((author_follow_count_new - author_follow_count), (user_follow_count_new - user_follow_count))
        self.assertEqual(user_follow_count_new, user_follow_count)

    def test_follow_index_with_correct_content(self):
        create_follow_url = reverse(f'posts:profile_follow', kwargs={'username': self.author.username,})
        create_follow_url_2 = reverse(f'posts:profile_follow', kwargs={'username': self.user.username,})
        """Подписались на автора и на пользователя"""
        self.auth_client.get(create_follow_url)
        self.auth_client_2.get(create_follow_url_2)
        """Разместили ПОСТ от имени автора"""
        form_data = {
            'text': 'Тестовый ПОСТ2',
            'group': f'{self.group.pk}',
        }
        self.author_user = Client()
        self.author_user.force_login(self.author)
        self.author_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_case = self.author.posts.first()
        """Зашли в подписки и увидели новый ПОСТ там где он должен быть"""
        response = self.auth_client.get('/follow/')
        form_field = response.context.get('page_obj')
        self.assertIn(post_case, form_field)
        """Зашли в подписки и не увидели новый ПОСТ там где его быть не должно"""
        response = self.auth_client_2.get('/follow/')
        form_field = response.context.get('page_obj')
        self.assertNotIn(post_case, form_field)