from django.urls import path
from .views import connection_test

urlpatterns = [
    # This makes the endpoint available at /api/data-endpoint/
    path('data-endpoint/', connection_test, name='test-connection'),
]