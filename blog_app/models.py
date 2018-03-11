from django.contrib.auth.models import User
from django.db import models
from django.utils.text import Truncator


class Post(models.Model):
    """Model for posts in the blog"""
    title = models.CharField(max_length=254)
    publ_date = models.DateTimeField(auto_now_add=True)
    post_text = models.TextField()
    before_spoiler = models.TextField(default='The post do not have a brief description.')

    def __str__(self):
        return self.title

class Comment(models.Model):
    """Model for comments in the blog"""
    # on_delete=models.SET_NULL assign NULL to the record if the post with
    # this comment is deleted (doesn't work without null=True),
    # related_name is for a reverse relationship (to get all the comments for the post)
    post_id = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True,
                                related_name='post_comments')
    # If we don't need a reverse relationship, '+'
    # With some DBs on_delete=models.DO_NOTHING may cause referential integrity
    # errors, SQLite is ok about that (as far as I know)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='+')
    publ_date = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField()

    def __str__(self):
        return Truncator(self.comment_text).chars(50)

# After implementing the models, we need to apply this changes to the db, for that
# py manage.py makemigrations
# py manage.py migrate
