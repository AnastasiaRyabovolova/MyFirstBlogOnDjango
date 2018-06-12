# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Profile, User, Reader, Subject
from .models import Board, Topic, Post, Action, Country, City
from django.contrib import admin

# Register your models here.
admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Action)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(Reader)
admin.site.register(Subject)
