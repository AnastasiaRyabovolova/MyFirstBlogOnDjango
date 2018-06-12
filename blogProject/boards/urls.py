from django.conf.urls import url
from boards import views
from accounts import views as accounts_views

urlpatterns = [
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name='new_topic'),

    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/reply/$',
        views.reply_topic,
        name='reply_topic'),

    url(r'^new_post/$', views.NewPostView.as_view(), name='new_post'),

    url(r'^board/create/$', views.create_board, name='create_board'),

    url(r'^board/(?P<pk>\d+)/edit$',
        views.edit_board,
        name='edit_board'),

    url(r'^board/(?P<pk>\d+)/delete$',
        views.delete_board,
        name='delete_board'),

    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/posts/(?P<post_pk>\d+)/edit/$',
        views.PostUpdateView.as_view(),
        name='edit_post'),
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/$',
        views.topic_posts,
        name='topic_posts'),

    url(r'^boards/(?P<pk>\d+)/$',
        views.TopicListView.as_view(),
        name='board_topics'),

]
