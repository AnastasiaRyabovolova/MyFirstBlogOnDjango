from django import forms
from .models import Topic, Post, Board


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
            widget=forms.Textarea(
                attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
            ),
            max_length=4000,
            help_text='The max length of the text is 4000.')

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class PostForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
             attrs={'rows': 5, 'id': 'post-text'},
            ),)

    class Meta:
        model = Post
        fields = ['message', ]


class BoardForm(forms.ModelForm):
    description = forms.CharField(
            widget=forms.Textarea(
                attrs={'rows': 5, 'placeholder': "What is board's description?"}
            ),
            max_length=4000)

    class Meta:
        model = Board
        fields = ['name', 'description', 'subject']
