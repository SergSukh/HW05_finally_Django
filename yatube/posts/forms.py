from xml.etree.ElementTree import Comment
from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': ('Текст нового поста:'),
            'group': ('Группа:'),
        }
        help_texts = {
            'text': ('Тут должен быть текст поста'),
            'group': ('Тут может быть группа'),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
