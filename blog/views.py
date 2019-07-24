from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, PostView, SavePost, Comment, LikeComment,sendNotif
from .forms import CommentForm, PostForm


from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET', 'POST', ])
def like_comment(request, pk):
    comment_pk = request.GET.get('comment_pk', -1)
    userId = request.user.id
    flag = True
    if LikeComment.objects.filter(comment_id=comment_pk).filter(user_id=userId).first():
        flag = False
    if flag:
        ap = LikeComment(comment=Comment.objects.get(id=comment_pk), user=User.objects.get(id=userId))
        ap.save()
    else:
        liked_comment = LikeComment.objects.filter(comment_id=comment_pk).filter(user_id=userId).first()
        liked_comment.delete()

    likes_count = LikeComment \
        .objects \
        .filter(comment_id=comment_pk) \
        .count()

    data = {
        "id": comment_pk,
        "like_Dislike": flag,
        "likes_count": likes_count
    }
    return Response(data)


@api_view(['GET', 'POST', ])
def dislike_comment(request, pk):
    comment_pk = username = request.GET.get('comment_pk', -1)
    print("hellooo", comment_pk)
    userId = request.user.id
    flag = True
    if LikeComment.objects.filter(comment_id=comment_pk).filter(user_id=userId).first():
        flag = False
    if flag:
        ap = LikeComment(comment=Comment.objects.get(id=comment_pk), user=User.objects.get(id=userId))
        ap.save()
    else:
        liked_comment = LikeComment.objects.filter(comment_id=comment_pk).filter(user_id=userId).first()
        liked_comment.delete()

    likes_count = LikeComment \
        .objects \
        .values('comment_id') \
        .annotate(Count('comment_id')) \
        .filter(comment_id=comment_pk) \
        .first()
    if likes_count:
        likes_count = likes_count.get('comment_id__count')
    else:
        likes_count = 0

    data = {
        "like_Dislike": flag,
        "likes_count": likes_count
    }
    return Response(data)


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title')) \
        .order_by('categories__title__count') \
        .reverse()
    return queryset


def save_post(request, pk):
    userId = request.user.id
    flag = True
    for p in SavePost.objects.filter(post_id=pk):
        if p.user_id == userId:
            flag = False
    if flag:
        ap = SavePost(post=Post.objects.get(id=pk), user=User.objects.get(id=userId))
        ap.save()
    return redirect(request.META.get('HTTP_REFERER'))


def un_save_post(request, pk):
    userId = request.user.id
    saved_post = SavePost.objects.filter(post_id=pk).filter(user_id=userId).first()
    saved_post.delete()
    return redirect(reverse('post-detail', kwargs={'pk': pk}))

def sendcomment(request , post, data):
    postid = post.id
    text = data['content']
    sn = sendNotif(post= Post.objects.get(id=postid) , user=User.objects.get(id=request.user.id), dateposted= 0, Text=text)
    sn.save()
    return redirect(request.META.get('HTTP_REFERER'))

def sendrate(request, post):
    postid = post.id
    text = "rate"
    sn = sendNotif(post= Post.objects.get(id=postid) , user=User.objects.get(id=request.user.id), dateposted= 0, Text=text)
    sn.save()
    return redirect(request.META.get('HTTP_REFERER'))

def my_notif(request):
    notifs = sendNotif.objects.all()
    for n in notifs:
        if n.post.author == request.user:
            if n.seen == False:
                n.seen = True
                n.save()

    context = {
        'notifications':sendNotif.objects.all()
    }
    return render(request, 'blog/notif.html', context)

def post_is_saved(pk, user):
    queryset = SavePost \
        .objects \
        .filter(user=user) \
        .filter(post_id=pk)
    flag = False
    if queryset:
        flag = True
    return flag


def do_like_comment(userId, comments):
    return_value = [False] * len(comments)
    i = 0
    for c in comments:
        if LikeComment.objects.filter(comment_id=c.id).filter(user_id=userId).first():
            return_value[i] = True
        i += 1
    print(return_value[::-1])
    return return_value[::-1]


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 4

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-date_posted')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['category_count'] = category_count
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post.html'
    context_object_name = 'post'
    form = CommentForm()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user=self.request.user,
                post=obj
            )
        return obj

    def get_context_data(self, **kwargs):
        is_saved = False
        do_like_comments = []
        if self.request.user.is_authenticated:
            post = self.get_object()
            is_saved = post_is_saved(post.pk, self.request.user)
            do_like_comments = do_like_comment(self.request.user.id, post.get_comments)
        context = super().get_context_data(**kwargs)
        context['is_saved'] = is_saved
        context['do_like_comments'] = do_like_comments
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            sendcomment(request,post, form.data)
            return redirect(reverse("post-detail", kwargs={
                'pk': post.pk
            }))


class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = request.user
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "blog/post_create.html", context)


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = request.user
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "blog/post_create.html", context)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def search(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        submitbutton = request.GET.get('submit')

        if query is not None:
            lookups = Q(username__icontains=query)

            results = User.objects.filter(lookups).distinct()

            context = {'results': results,
                       'submitbutton': submitbutton}
            return render(request, 'blog/search.html', context)

        else:
            return render(request, 'blog/search.html')

    else:
        return render(request, 'blog/search.html')


def blog_search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).distinct()

    flag = False
    if request.GET.get('blog_search_submit') == 'blog_search':
        flag = True
    context = {
        'posts': queryset.order_by('-date_posted'),
        'blog_search': flag
    }
    return render(request, 'blog/blog_search_results.html', context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
