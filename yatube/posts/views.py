from django.shortcuts import render
from .models import Post


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts,
    }
    return render(request, template, context)


def group_posts(request):
    template = 'posts/group_list.html'
    text = 'Информация на странице группы будет тут.'
    context = {
        'text': text,
    }
    return render(request, template, context)
