from rest_framework.routers import DefaultRouter
from .views import JournalEntryViewSet
router = DefaultRouter()
router.register(r'journal', JournalEntryViewSet, basename='journal')
urlpatterns = router.urls
