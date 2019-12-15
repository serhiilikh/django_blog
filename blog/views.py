from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Post, Comment
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import CommentForm
from .forms import UserForm, ProfileForm, PostCreationForm, UserActivationForm
from django.contrib.auth.models import Group, Permission
from uuid import uuid4
import pika
from json import dumps

def post_list(request):
    return render(request, "posts.html", {"posts": Post.objects.all().filter(is_published=True)})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.all().filter(post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment()
            new_comment.text = form.cleaned_data['text']
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()

            notification = {'email': post.user.username,
                            'subject': 'New comment',
                            'message': 'You have new comment in your post "{}"'.format(post.title)}
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.basic_publish(exchange='', routing_key='email_queue', body=dumps(notification))
            connection.close()

            return HttpResponseRedirect(request.path_info)
    else:
        form = CommentForm()
    if request.user.is_authenticated:
        return render(request, 'post_detail.html', {'form': form, 'post': post, 'comments': comments})
    else:
        return render(request, 'post_detail.html', {'post': post, 'comments': comments})


@transaction.atomic
def signup(request):
    users, created = Group.objects.get_or_create(name='users')
    redactors, created = Group.objects.get_or_create(name='redactors')
    admins, created = Group.objects.get_or_create(name='admins')
    perm = Permission.objects.get(name='Can publish post')
    admins.permissions.add(perm)
    redactors.permissions.add(perm)

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = User.objects.create(first_name=user_form.cleaned_data['first_name'],
                                       last_name=user_form.cleaned_data['last_name'],
                                       username=user_form.cleaned_data['username'],
                                       is_active=False)
            user.set_password(user_form.cleaned_data['password'])
            user.profile.birth_date = profile_form.cleaned_data['birth_date']
            code = uuid4()
            user.profile.activation_code = code
            user.save()

            notification = {'email': user.username,
                            'subject': 'Activation code',
                            'message': 'Code: {}'.format(code)}
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.basic_publish(exchange='', routing_key='email_queue', body=dumps(notification))
            connection.close()


            return redirect('/wait_for_email/')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'registration/sign_up.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def create_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostCreationForm(request.POST)
            if form.is_valid():
                post = Post(content=form.cleaned_data['content'],
                            title=form.cleaned_data['title'],
                            user=request.user,
                            is_published=True if request.user.has_perm('publish_post') else False)
                post.save()
                return redirect('/')
        else:
            form = PostCreationForm(request.POST)
            return render(request, 'create_post.html', {'form': form})


def wait_for_email(request):
    if request.method == 'POST':
        form = UserActivationForm(request.POST)
        if form.is_valid():
            user = User.objects.get(profile__activation_code=form.cleaned_data['code'])
            if user:
                user.is_active = True
                user.profile.activation_code = ''
                return redirect('registration_success')
            else:
                return render(request, 'registration/wait_for_email.html', {'response': 'Error, invalid code'})
    else:
        form = UserActivationForm()
        return render(request, 'registration/wait_for_email.html', {'form': form})


def registration_success(request):
    return render(request, 'registration/signup_success.html')
