# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from boards.models import Board, Topic
from api.serializers import BoardSerializer, TopicSerializer, UserSerializer
from rest_framework.authentication import SessionAuthentication
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework import generics
from boards.models import User
from rest_framework import permissions

# Create your views here.


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TopicList(APIView):

    def get(self, request, format=None):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if 'board_id' not in request.data.keys():
            board = Board.objects.create(name=request.data['board']['name'],
                                         description=request.data['board']['description'],
                                         creater=request.user)
            board.save()
            request.data['board_id'] = board.pk

        request.data['starter'] = request.user
        topic_serializer = TopicSerializer(data=request.data)
        if topic_serializer.is_valid():
            topic_serializer.save(board_id=request.data['board_id'], starter=request.user)
            return Response(topic_serializer.data, status=status.HTTP_201_CREATED)
        return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicDetail(APIView):

    def get_object(self, pk):
        return get_object_or_404(Topic, pk=pk)

    def get(self, request, pk, format=None):
        serializer = TopicSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        topic = self.get_object(pk)
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        topic = self.get_object(pk)
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BoardList(APIView):

    def get(self, request, format=None):
        boards = Board.objects.all()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        request.data['creater'] = request.user.username
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creater=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class BoardDetail(APIView):

    def get_object(self, pk):
        return get_object_or_404(Board, pk=pk)

    def get(self, request, pk, format=None):
        serializer = BoardSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        board = self.get_object(pk)
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        board = self.get_object(pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExampleView(APIView):

    def get(self, request, format=None):
        content = {
            'user': unicode(request.user),
            'auth': unicode(request.auth),  # None
        }
        return Response(content)
