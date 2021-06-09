from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Post, User


def index(request):
    post_list = Post.objects.prefetch_related(
        'comments', 'author', 'group'
    ).all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "index.html", {"page": page})


def profile(request, username):
    author_object = get_object_or_404(User, username=username)
    post_list = author_object.posts.select_related(
        'author', 'group'
    ).prefetch_related('comments').all()

    paginator = Paginator(post_list, settings.POSTS_PER_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    is_subscribed = False
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author_object).exists():
            is_subscribed = True

    followers = Follow.objects.filter(author=author_object.pk).count()
    follows = Follow.objects.filter(user=author_object.pk).count()

    return render(
        request,
        'posts/profile.html',
        {'username': author_object,
         'page': page,
         'form': form,
         'is_comment': False,
         'following': is_subscribed,
         'followers': followers,
         'follows': follows
         }
    )


def post_view(request, username, post_id):
    user_object = get_object_or_404(User, username=username)
    post_object = get_object_or_404(Post, author=user_object, id=post_id)
    comments = post_object.comments.all()

    form = CommentForm()

    followers = Follow.objects.filter(author=user_object.pk).count()
    follows = Follow.objects.filter(user=user_object.pk).count()

    return render(request, 'posts/post.html',
                  {'username': user_object,
                   'post': post_object,
                   'comments': comments,
                   'form': form,
                   'is_comment': True,
                   'followers': followers,
                   'follows': follows})


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    return render(request,
                  'posts/new_edit_post.html',
                  {'form': form})


@login_required
def post_edit(request, username, post_id):
    post_object = get_object_or_404(
        Post.objects.select_related('author'), pk=post_id
    )

    if post_object.author != request.user:
        return redirect('post', username=username, post_id=post_object.id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_object)
    if form.is_valid():
        form.save()
        return redirect('post',
                        post_object.author.username,
                        post_object.id)

    return render(request,
                  'posts/new_edit_post.html',
                  {'form': form, 'post': post_object})


def page_not_found(request, exception):
    return render(request,
                  "posts/misc/404.html",
                  {"path": request.path},
                  status=404)


def server_error(request):
    return render(request, "posts/misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post_author = get_object_or_404(User, username=username)
    post_object = get_object_or_404(Post, author=post_author, id=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post_object
        comment.save()

    return redirect('post',
                    post_author.username,
                    post_object.id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related(
        'author', 'group'
    ).prefetch_related(
        'comments'
    ).filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return(render(request, 'follow.html', {"page": page,
                                           "username": request.user}))


@login_required
def profile_follow(request, username):
    author_obj = get_object_or_404(User, username=username)
    if request.user == author_obj:
        return(redirect('profile', username))
    request.user.follower.get_or_create(author=author_obj)

    return(redirect('profile', username))


@login_required
def profile_unfollow(request, username):
    author_obj = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author_obj).delete()
    return(redirect('profile', username))
