from django.contrib import admin
from .models import Category, Post, Comment, Location, SavePost, LikeComment, DislikeComment

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Location)
admin.site.register(SavePost)
admin.site.register(LikeComment)
admin.site.register(DislikeComment)

