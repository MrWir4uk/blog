from django.contrib import admin
from .models import Profile, Category, Tag, Post, Comment, Rating

# Register your models here.
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Rating)

