from django import forms
from blog.models import Comment, Post, Profile
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.Form):
    username = forms.EmailField(label='Email', max_length=200)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    first_name = forms.CharField(label='First name', max_length=100, required=False)
    last_name = forms.CharField(label='Last name', max_length=100, required=False)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date',)


class PostCreationForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget, label='')

    class Meta:
        model = Post
        fields = ('title', 'content')


class UserActivationForm(forms.Form):
    code = forms.CharField(required=True, max_length=36)

