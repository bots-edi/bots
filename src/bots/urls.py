# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views

admin.autodiscover()

staff_required = user_passes_test(lambda u: u.is_staff)

superuser_required = user_passes_test(lambda u: u.is_superuser)

run_permission = user_passes_test(lambda u: u.has_perm("bots.change_mutex"))

urlpatterns = [
    url(r"^login.*", auth_views.LoginView.as_view(template_name="admin/login.html")),
    url(r"^logout.*", auth_views.LogoutView.as_view(next_page="/")),
    url(
        r"^password_change/$",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    url(
        r"^password_change/done/$",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    # login required
    url(r"^home.*", login_required(views.home)),
    url(r"^incoming.*", login_required(views.incoming)),
    url(r"^detail.*", login_required(views.detail)),
    url(r"^process.*", login_required(views.process)),
    url(r"^outgoing.*", login_required(views.outgoing)),
    url(r"^document.*", login_required(views.document)),
    url(r"^reports.*", login_required(views.reports)),
    url(r"^confirm.*", login_required(views.confirm)),
    url(r"^filer.*", login_required(views.filer)),
    url(r"^srcfiler.*", login_required(views.srcfiler)),
    url(r"^logfiler.*", login_required(views.logfiler)),
    # only staff
    url(r"^admin/$", login_required(views.home)),  # do not show django admin root page
    url(
        r"^admin/bots/$", login_required(views.home)
    ),  # do not show django admin root page
    url(r"^admin/", include(admin.site.urls)),
    url(r"^runengine.+", run_permission(views.runengine)),
    # only superuser
    url(r"^delete.*", superuser_required(views.delete)),
    url(r"^plugin/index.*", superuser_required(views.plugin_index)),
    url(r"^plugin.*", superuser_required(views.plugin)),
    url(r"^plugout/index.*", superuser_required(views.plugout_index)),
    url(r"^plugout/backup.*", superuser_required(views.plugout_backup)),
    url(r"^plugout.*", superuser_required(views.plugout)),
    url(r"^sendtestmail.*", superuser_required(views.sendtestmailmanagers)),
    # catch-all
    url(r"^.*", views.index),
]

handler500 = views.server_error
