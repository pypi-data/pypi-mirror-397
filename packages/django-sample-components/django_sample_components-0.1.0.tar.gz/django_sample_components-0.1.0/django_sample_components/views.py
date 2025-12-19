from django.conf import settings
from django.shortcuts import render
from django.views import View


class Home(View):
    def get(self, request):
        context = {
            'url_pypi': settings.URL_PYPI,
            'url_github': settings.URL_GITHUB,
        }
        return render(request, 'django_sample_components/pages/home.html', context)


class Greeting(View):
    def get(self, request):
        return render(request, 'django_sample_components/pages/greeting.html')


class Alert(View):
    def get(self, request):
        return render(request, 'django_sample_components/pages/alert.html')
