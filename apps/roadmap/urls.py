from rest_framework.routers import DefaultRouter
from .views import RoadmapItemViewSet
router = DefaultRouter()
router.register(r'roadmap', RoadmapItemViewSet, basename='roadmap')
urlpatterns = router.urls
