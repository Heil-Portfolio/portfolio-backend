from rest_framework.routers import DefaultRouter
from .views import LabViewSet
router = DefaultRouter()
router.register(r'labs', LabViewSet, basename='labs')
urlpatterns = router.urls
