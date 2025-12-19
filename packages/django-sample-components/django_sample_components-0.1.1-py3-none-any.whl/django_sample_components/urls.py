from django.urls import path

from .views import Alert, Greeting, Home

app_name = 'django_sample_components'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('greeting/', Greeting.as_view(), name='greeting'),
    path('alert/', Alert.as_view(), name='alert'),
]
