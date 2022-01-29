from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'text': ('Текст нового поста:'),
            'group': ('Группа:'),
        }
        help_texts = {
            'text': ('Тут должен быть текст поста'),
            'group': ('Тут может быть группа'),
        }
