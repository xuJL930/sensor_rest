# -*- coding:utf8 -*-
from django.conf.urls import url
from . import views


urlpatterns = [
    url(
        r'^gateway/(?P<pk>\w+)/$', views.index, name='gateway'
    ),

    url(
        r'^terminals/$', views.get_post_terminal, name='get_post_terminal'
    ),
    url(
        r'^terminals/(?P<pk>\w+)/$', views.get_patch_single_terminal, name='get_patch_single_terminal'
    ),
    url(
        r'^terminals/(?P<pk>\w+)/led$', views.patch_led, name='patch_led'
    ),
    url(
        r'^terminals/\w+/reports/$', views.get_post_report, name='get_post_report'
    ),
    url(
        r'^terminals/\w+/reports/(?P<pk>\w+)/$', views.get_single_report, name='get_single_report'
    ),
    url(
        r'^users/$', views.get_post_user, name='get_post_user'
    ),
    url(
        r'^users/(?P<pk>\w+)/$', views.get_patch_single_user, name='get_patch_single_user'
    ),

    url(
        r'^gateways/$', views.get_post_gateway, name='get_post_gateway'
    ),
    url(
        r'^gateways/(?P<pk>\w+)/$', views.get_single_gateway, name='get_single_gateway'
    ),
    url(
        r'^gateways/\w+/reset/$', views.reset_gateway, name='reset_gateway'
    ),
    url(
        r'^gateways/(?P<pk>\w+)/node/$', views.post_node, name='post_node'
    ),
    url(
        r'^gateways/(?P<pk1>\w+)/node/(?P<pk2>\w+)/$', views.get_patch_node, name='get_patch_node'
    ),
]
