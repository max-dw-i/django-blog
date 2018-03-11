from django import forms

from .models import Comment
from .validators import validate_not_new_line


class NewCommentForm(forms.ModelForm):
    """Form for posting new comments"""
    class Meta:
        model = Comment
        fields = ['comment_text']

        widgets = {
            'comment_text': forms.Textarea(attrs={'placeholder': 'New comment...'}),
        }


class SendEmailForm(forms.Form):
    """Form for sending emails to the blog's author"""
    subject = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the subject...'}),
        validators=[validate_not_new_line],
    )
    email_from = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email...'}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter your message...'}),
        validators=[validate_not_new_line],
    )


class SearchForm(forms.Form):
    """Form for searching posts in the blog"""
    query = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Search...'}),
    )
