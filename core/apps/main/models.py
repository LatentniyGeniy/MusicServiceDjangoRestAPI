from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from core.apps.main.choices import ALBUM, RELEASE_TYPE_CHOICES


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **other_fields):
        
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email), **other_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password, **other_fields):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password, **other_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, default='user')
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Genre(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Artist(models.Model):
    title = models.CharField(max_length=255, unique=True)
    picture_link = models.CharField(max_length=255)
    genre = models.ManyToManyField(Genre)
    likes = GenericRelation(Like)


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ManyToManyField(Artist, related_name='albums')
    release_date = models.DateField()
    release_type = models.CharField(
        max_length=10,
        choices=RELEASE_TYPE_CHOICES,
        default=ALBUM,
    )
    genre = models.ManyToManyField(Genre)
    picture_link = models.CharField(max_length=255)
    likes = GenericRelation(Like)


class Song(models.Model):
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    genre = models.ManyToManyField(Genre)
    file_link = models.CharField(max_length=255)
    likes = GenericRelation(Like)


class Playlist(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_playlist')
    song = models.ManyToManyField(Song, related_name='song_playlist')
    likes = GenericRelation(Like)
