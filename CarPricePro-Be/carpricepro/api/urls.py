# api/urls.py
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, CarList, PredictPriceView
from django.urls import path, include

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Thêm tuyến đường cho CarList
    path('cars/', CarList.as_view(), name='car-list'),
    path('predict_price/', PredictPriceView.as_view(), name='predict_price'),

]
