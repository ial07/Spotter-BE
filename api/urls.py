from django.urls import path
from .views import CalculateTripAPIView

urlpatterns = [
    path('calculate-trip/', CalculateTripAPIView.as_view(), name='calculate-trip'),
]