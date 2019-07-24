from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse



class Location(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()

    def __str__(self):
        return str(self.x + self.y)


# class loc(models2.Model):
#     name = models.CharField(max_length=100)
#     location = models.PointField()


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to='post_image')
    content = models.TextField()
    # location = models.ForeignKey(Location, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(
        'Post', related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    @property
    def like_comment_count(self):
        return LikeComment.objects.filter(comment=self).count()

    @property
    def dislike_comment_count(self):
        return DislikeComment.objects.filter(comment=self).count()


class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username)


class DislikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username)


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return str(self.score)


class SavePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.post.content)

class sendNotif(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    Text = models.TextField()
    dateposted = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
