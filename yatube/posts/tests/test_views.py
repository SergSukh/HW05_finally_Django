from datetime import datetime
from random import random

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import POSTS_IN_PAGE
from .fixtures import constant_post

User = get_user_model()


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
        post = (Post(pk=i,
                     author=cls.user,
                     group=cls.group,
                     text=f'Тестовый текст{i}',
                     pub_date=datetime(2017, 1, i)
                     ) for i in range(1, 13)
                )
        cls.post = Post.objects.bulk_create(post)
        #  Страницы для тестирования:

        cls.non_paginator_pages_names = {
            'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': f'{cls.post[0].pk}'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': f'{cls.post[0].pk}'}),
        }

        cls.paginator_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': f'{cls.post[0].author}'}),
        }

        cls.test_group_page = {
            'posts/group_list.html':
            reverse('posts:group_post',
                    kwargs={'slug': f'{cls.post[0].group}'}),
        }

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = self.non_paginator_pages_names
        templates_pages_names.update(self.paginator_pages_names)
        templates_pages_names.update(self.test_group_page)
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        templates_pages_names = self.paginator_pages_names
        templates_pages_names.update(self.test_group_page)
        """Шаблон сформирован с правильным контекстом."""
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                rnd = Post.objects.count() - int(random() * 10)
                post_case = Post.objects.get(id=rnd)
                form_field = response.context.get('page_obj')
                self.assertIn(post_case, form_field)

    def test_first_page_contains_ten_records(self):
        templates_pages_names = self.paginator_pages_names
        templates_pages_names.update(self.test_group_page)
        post_in_pages = POSTS_IN_PAGE
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    post_in_pages)

    def test_second_page_contains_three_records(self):
        templates_pages_names = self.paginator_pages_names
        templates_pages_names.update(self.test_group_page)
        post_in_pages = POSTS_IN_PAGE
        posts_finish_page = Post.objects.count() % post_in_pages
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get((reverse_name) + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    posts_finish_page)

    def test_create_new_post_with_test_group(self):
        """Валидная форма создает запись в Post с Новой группой"""
        post_count = Post.objects.count()
        self.group = Group.objects.create(
            title='2я Тестовая Группа',
            slug='2Test_group',
            description='дополнительный тест',
        )
        form_data = {
            'text': 'Тестовый текст2',
            'group': f'{self.group.pk}',
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        """Проверяем, что запись произошла"""
        self.assertEqual(post_count + 1, Post.objects.count())
        """Проверяем соответствующие страницы"""
        self.second_test_group = {
            'posts/group_list.html':
            reverse('posts:group_post',
                    kwargs={'slug': f'{self.group.slug}'}),
        }
        templates_pages_names = self.paginator_pages_names
        templates_pages_names.update(self.second_test_group)
        post_case = Post.objects.get(id=post_count + 1)
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertIn(
                    post_case,
                    response.context.get('page_obj'))
