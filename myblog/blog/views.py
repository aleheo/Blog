from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.
def post_list(request) -> HttpResponse:
    posts = Post.published.all()
    return render(request, 
                  'blog/post/list.html', 
                  {'posts': posts})

def post_detail(request, id) -> HttpResponse:
    post = get_object_or_404(Post,
                             id=id,
                             status=Post.Status.PUBLISHED)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})