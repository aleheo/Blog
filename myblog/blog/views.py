from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

class PostListView(ListView):
    '''
    Alternate list view
    '''
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request) -> HttpResponse:
    post_list = Post.published.all()
    # Pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 
                  'blog/post/list.html', 
                  {'posts': posts})

def post_detail(request, year, month, day, slug) -> HttpResponse:
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев
    comments = post.comments.filter(active=True)
    # Форма для создания комментариев
    form = CommentForm()
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form})

def post_share(request, post_id) -> HttpResponse:
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    
    sent = False
    
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recomends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 
                  'blog/post/share.html', 
                  {'post': post, 
                   'form': form,
                   'sent': sent})

@require_POST
def post_comment(request, post_id) -> HttpResponse | None:
    post = get_object_or_404(Post,
                             id = post_id,
                             status=Post.Status.PUBLISHED)
    
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Связать комментарий с постом
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
        return render(request, 'blog/post/comment.html',
                      {'post': post,
                       'form': form,
                       'comment': comment})