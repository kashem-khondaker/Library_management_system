from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowRecordViewSet

# Create a router and register the BorrowRecordViewSet
router = DefaultRouter()
router.register(r'borrow-records', BorrowRecordViewSet, basename='borrowrecord')

urlpatterns = [
    path('', include(router.urls)),
]
