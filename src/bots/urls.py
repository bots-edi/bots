# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import include
from django.contrib import auth
from django.urls import path
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views

admin.autodiscover()

staff_required = user_passes_test(lambda u: u.is_staff)

superuser_required = user_passes_test(lambda u: u.is_superuser)

run_permission = user_passes_test(lambda u: u.has_perm('bots.change_mutex'))

urlpatterns = [
    path(r'^login.*', auth.login, {'template_name': 'admin/login.html'}),
    path(r'^logout.*', auth.logout, {'next_page': '/'}),
    # path(r'^password_change/$', auth., name='password_change'),
    #  path(r'^password_change/done/$', auth.views.password_change_done, name='password_change_done'),
    # login required
    path(r'^home.*', login_required(views.home)),
    path(r'^incoming.*', login_required(views.incoming)),
    path(r'^detail.*', login_required(views.detail)),
    path(r'^process.*', login_required(views.process)),
    path(r'^outgoing.*', login_required(views.outgoing)),
    path(r'^document.*', login_required(views.document)),
    path(r'^reports.*', login_required(views.reports)),
    path(r'^confirm.*', login_required(views.confirm)),
    path(r'^filer.*', login_required(views.filer)),
    path(r'^srcfiler.*', login_required(views.srcfiler)),
    path(r'^logfiler.*', login_required(views.logfiler)),
    # only staff
    path(r'^admin/$', login_required(views.home)),  # do not show django admin root page
    path(r'^admin/bots/$', login_required(views.home)),  # do not show django admin root page
    path(r'^admin/', include(admin.site.paths)),
    path(r'^runengine.+', run_permission(views.runengine)),
    # only superuser
    path(r'^delete.*', superuser_required(views.delete)),
    path(r'^plugin/index.*', superuser_required(views.plugin_index)),
    path(r'^plugin.*', superuser_required(views.plugin)),
    path(r'^plugout/index.*', superuser_required(views.plugout_index)),
    path(r'^plugout/backup.*', superuser_required(views.plugout_backup)),
    path(r'^plugout.*', superuser_required(views.plugout)),
    path(r'^sendtestmail.*', superuser_required(views.sendtestmailmanagers)),
    # catch-all
    path(r'^.*', views.index),
]

handler500 = views.server_error
