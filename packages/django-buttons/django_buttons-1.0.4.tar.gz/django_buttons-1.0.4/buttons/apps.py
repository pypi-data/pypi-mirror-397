"""
Django application config.

:creationdate: 09/02/17 15:47
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: buttons.apps

"""

import logging

from django.apps import AppConfig

__author__ = "fguerin"
logger = logging.getLogger("buttons.apps")


class ButtonsAppConfig(AppConfig):
    """:mod:`buttons` application settings."""

    #: Application name
    name = "buttons"

    def ready(self):
        """Application is ready."""
        super().ready()
        from buttons.conf import ButtonsAppConf  # noqa
