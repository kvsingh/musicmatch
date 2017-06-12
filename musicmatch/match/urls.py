from django.conf.urls import url
from match import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
