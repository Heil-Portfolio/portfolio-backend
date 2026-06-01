from rest_framework.routers import DefaultRouter
from .views import WalkthroughViewSet
router = DefaultRouter()
router.register(r'walkthroughs', WalkthroughViewSet, basename='walkthroughs')
urlpatterns = router.urls
