from rest_framework import serializers
from boards.models import Board, Topic
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    boards = serializers.PrimaryKeyRelatedField(many=True, queryset=Board.objects.all())
    topics = serializers.PrimaryKeyRelatedField(many=True, queryset=Topic.objects.all())
    # token = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'boards')


class BoardSerializer(serializers.ModelSerializer):
    creater = serializers.StringRelatedField(many=False)

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'creater', 'is_deleted',)

    def create(self, validated_data):
        return Board.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.creater = validated_data.get('creater', instance.creater)
        instance.save()
        return instance


class TopicSerializer(serializers.ModelSerializer):
    starter = serializers.StringRelatedField(many=False)
    board_id = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Topic
        fields = ('id', 'subject', 'board_id', 'last_updated', 'starter', 'views')

    def create(self, validated_data):
        return Topic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.subject = validated_data.get('subject', instance.subject)
        instance.board = validated_data.get('board', instance.board)
        instance.starter = validated_data.get('starter', instance.starter)
        instance.last_update = validated_data.get('last_updated', instance.last_updated)
        instance.save()
        return instance
