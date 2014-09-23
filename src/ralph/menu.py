# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from bob.menu import MenuItem
from ralph.account.models import Perm
from ralph.scan.util import get_pending_scans


class Menu(object):
    module = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs
        profile = self.request.user.get_profile()
        self.has_perm = profile.has_perm

    def generate_menu_items(self, data):
        return [MenuItem(**t) for t in data]

    def get_module(self):
        if not self.module:
            raise ImproperlyConfigured(
                'Menu required definition of \'module\' or an implementation '
                'of \'get_module()\'')

        if not isinstance(self.module, MenuItem):
            raise ImproperlyConfigured(
                'Module must inheritence from \'MenuItem\'')

        return self.module

    def get_active_submodule(self):
        if not self.submodule:
            raise ImproperlyConfigured(
                'Menu required definition of \'submodule\' or an '
                'implementation of \'get_active_submodule()\'')

        if not isinstance(self.submodule, MenuItem):
            raise ImproperlyConfigured(
                'submodule must inheritence from \'MenuItem\'')

        return self.submodule

    def get_submodules(self):
        return []

    def get_sidebar_items(self):
        return {}


class CoreMenu(Menu):
    module = MenuItem(
        'Core',
        name='module_core',
        fugue_icon='fugue-processor',
        view_name='ventures',
    )

    def __init__(self, *args, **kwargs):
        self.venture = None
        self.object = None
        super(CoreMenu, self).__init__(*args, **kwargs)

    def get_submodules(self):
        submodules = []
        if self.has_perm(Perm.has_core_access):
            submodules.append(
                MenuItem(
                    _('Ventures'),
                    fugue_icon='fugue-store',
                    view_name='ventures',
                )
            )
        if self.has_perm(Perm.read_dc_structure):
            submodules.append(
                MenuItem(_('Racks'), fugue_icon='fugue-building',
                         view_name='racks'))
        if self.has_perm(Perm.read_network_structure):
            submodules.append(
                MenuItem(_('Networks'), fugue_icon='fugue-weather-clouds',
                         view_name='networks'))
        submodules.append(
            MenuItem(_('Ralph CLI'), fugue_icon='fugue-terminal',
                     href='#beast'))
        submodules.append(
            MenuItem(_('Quick scan'), fugue_icon='fugue-radar',
                     href='#quickscan'))
        submodules.append(
            MenuItem(_('Search'), fugue_icon='fugue-application-search-result',
                     view_name='search', name='search'))

        pending_scans = get_pending_scans()
        if pending_scans:
            submodules.append(MenuItem(
                _('Pending scans {}/{}').format(
                    pending_scans.new_devices,
                    pending_scans.changed_devices,
                ),
                view_kwargs={'scan_type': (
                    'new' if pending_scans.new_devices else 'existing'
                )},
                name='scan_list',
                view_name='scan_list',
                fugue_icon='fugue-light-bulb--exclamation',
            ))
        return submodules

    def get_sidebar_items(self):
        return {}

menu_class = CoreMenu