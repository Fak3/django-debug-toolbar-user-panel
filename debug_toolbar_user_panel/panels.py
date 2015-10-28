"""
:mod:`django-debug-toolbar-user-panel`
======================================

Panel for the `Django Debug Toolbar <https://github.com/django-debug-toolbar/django-debug-toolbar>`_
to easily and quickly switch between users.

 * View details on the currently logged in user.
 * Login as any user from an arbitrary email address, username or user ID.
 * Easily switch between recently logged in users.

.. figure::  screenshot.png
   :align:   center

The panel supports ``django.contrib.auth.models.User`` models that have had
the `username` field removed.

Installation
------------

Add ``debug_toolbar_user_panel`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'debug_toolbar_user_panel',
        ...
    )

Add ``debug_toolbar_user_panel.panels.UserPanel`` to ``DEBUG_TOOLBAR_PANELS``::

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar_user_panel.panels.UserPanel'
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

Include ``debug_toolbar_user_panel.urls`` somewhere in your ``urls.py``::

    urlpatterns = patterns('',
        ...
        url(r'', include('debug_toolbar_user_panel.urls')),
        ...
    )

Links
-----

View/download code
  https://github.com/playfire/django-debug-toolbar-user-panel

File a bug
  https://github.com/playfire/django-debug-toolbar-user-panel/issues
"""

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url


class UserPanel(DebugPanel):
    """
    Panel that allows you to login as other recently-logged in users.
    """

    name = 'User'
    has_content = True

    def nav_title(self):
        return _('User')

    def url(self):
        return ''

    def title(self):
        return _('User')

    def nav_subtitle(self):
        return self.request.user.is_authenticated() and self.request.user

    def process_response(self, request, response):
        from django.contrib.auth.models import User
        from .forms import UserForm

        self.request = request

        current = []

        if request.user.is_authenticated():
            for field in User._meta.fields:
                if field.name == 'password':
                    continue
                current.append(
                    (field.attname, getattr(request.user, field.attname))
                )

        self.record_stats({
            'form': UserForm(),
            'next': request.GET.get('next'),
            'users': User.objects.order_by('-last_login')[:10],
            'current': current,
        })

    template = 'debug_toolbar_user_panel/content.html'

    @classmethod
    def get_urls(cls):
        return patterns('debug_toolbar_user_panel.views',
            url(r'/users/$', 'content', name='debug-userpanel'),
            url(r'/users/login/$', 'login_form', name='debug-userpanel-login-form'),
            url(r'/users/login/(?P<pk>-?\d+)$', 'login', name='debug-userpanel-login'),
            url(r'/users/logout$', 'logout', name='debug-userpanel-logout'),
        )

