from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'boards', views.BoardViewSet, basename='board')
router.register(
    r'boards/(?P<board_ln>[^/.]+)/threads', views.ThreadViewSet, basename='thread')
router.register(
    r'boards/(?P<board_ln>[^/.]+)/posts', views.PostViewSet, basename='post')
router.register(r'', views.IndexViewSet, basename='index')

urlpatterns = router.urls
