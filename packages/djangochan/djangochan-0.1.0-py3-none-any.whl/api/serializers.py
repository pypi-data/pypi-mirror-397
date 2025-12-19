from rest_framework import serializers

from core.models import Board, Post


# TODO: optional add few replies in every thread returned
class IndexSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    last_reply_timestamp = serializers.SerializerMethodField()
    board = serializers.CharField(source='board.ln')

    class Meta:
        model = Post
        fields = [
            'board',
            'url', 'pk', 'subject',
            'timestamp', 'author', 'tripcode', 'text',
            'image', 'filename',
            'replies_count', 'last_reply_timestamp',
        ]

    def get_url(self, obj):
        return '/api/boards/' + obj.board.ln + '/threads/' + str(obj.pk)

    def get_replies_count(self, obj):
        return obj.post_set.count()

    def get_last_reply_timestamp(self, obj):
        post_obj = obj.post_set.last()
        return post_obj.timestamp if post_obj is not None else ''


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    last_post_timestamp = serializers.SerializerMethodField()
    last_thread_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'url', 'ln', 'name', 'description',
            'last_post_timestamp', 'last_thread_timestamp',
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'ln'}
        }

    def get_last_post_timestamp(self, obj):
        post_obj = obj.post_set.last()
        return post_obj.timestamp if post_obj is not None else ''

    def get_last_thread_timestamp(self, obj):
        post_obj = obj.post_set.filter(thread__isnull=True).last()
        return post_obj.timestamp if post_obj is not None else ''


# TODO: optional add few replies in every thread returned
class ThreadSerializer(serializers.HyperlinkedModelSerializer):
    replies_count = serializers.SerializerMethodField()
    last_reply_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'url', 'pk', 'subject',
            'timestamp', 'author', 'tripcode', 'text',
            'image', 'filename',
            'closed', 'sticky',
            'replies_count', 'last_reply_timestamp',
        ]

    def get_replies_count(self, obj):
        return obj.post_set.count()

    def get_last_reply_timestamp(self, obj):
        post_obj = obj.post_set.last()
        return post_obj.timestamp if post_obj is not None else ''


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'url', 'pk',  # 'thread', 'subject',
            'timestamp', 'author', 'tripcode', 'text',
            'image', 'filename',
        ]


class PostSerializer(serializers.ModelSerializer):
    # XXX: if done similar to forms by inheriting and excluding
    # following assertion error happens
    # > Cannot set both 'fields' and 'exclude' options on serializer <name>.
    # so it's kinda done the other way around
    class Meta:
        model = Post
        fields = ReplySerializer.Meta.fields + [
            'thread', 'subject',
        ]
