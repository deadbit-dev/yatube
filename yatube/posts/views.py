from django.http import HttpResponse
from django.shortcuts import resolve_url


def index(request):
    return HttpResponse('Main page')

def group_posts(request, slug):
    return HttpResponse(f'Here living your post 😉 {slug}')
