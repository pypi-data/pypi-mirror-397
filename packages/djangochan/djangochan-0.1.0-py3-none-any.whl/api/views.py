from rest_framework import viewsets
from rest_framework.response import Response

from core.models import Board, Post
from . import serializers


class IndexViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(thread__isnull=True).order_by('-bump')[:5]
    serializer_class = serializers.IndexSerializer


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = serializers.BoardSerializer
    lookup_field = 'ln'


class ThreadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = serializers.ThreadSerializer

    def list(self, request, board_ln=None):
        queryset = Post.objects.filter(
            board__ln=board_ln, thread__isnull=True).order_by('-bump')
        serializer = serializers.ThreadSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, board_ln=None, pk=None):
        queryset = Post.objects.filter(thread=pk).order_by('timestamp')
        serializer = serializers.ReplySerializer(queryset, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer

    def list(self, request, board_ln=None):
        return Response({})

    def retrieve(self, request, board_ln=None, pk=None):
        queryset = Post.objects.get(
            board__ln=board_ln, pk=pk)
        serializer = serializers.PostSerializer(queryset)
        return Response(serializer.data)
