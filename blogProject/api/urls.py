from django.conf.urls import include
from django.conf.urls import url
from api import views
from rest_framework.authtoken import views as token_view


urlpatterns = [
    url(r'^boards/$', views.BoardList.as_view()),
    url(r'^boards/(?P<pk>\d+)/$', views.BoardDetail.as_view()),
    url(r'^topics/$', views.TopicList.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^exp/$', views.ExampleView.as_view()),
    url(r'^topics/(?P<pk>\d+)/$', views.TopicDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-token-auth/', token_view.obtain_auth_token),

]
