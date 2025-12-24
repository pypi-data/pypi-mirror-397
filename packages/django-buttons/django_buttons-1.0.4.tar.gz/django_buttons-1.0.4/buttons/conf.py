"""
Configuration values for the :mod:`buttons:buttons` application.

:creationdate: 09/01/17 12:48
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: buttons.conf

"""

import logging

from appconf import AppConf

__author__ = "fguerin"
logger = logging.getLogger("buttons.conf")


class ButtonsAppConf(AppConf):
    """App con for :mod:`buttons:buttons` application."""

    #: Icon position, between `START` and `END`
    ICON_POSITION: str = "END"

    #: Default icon
    ICON: str = "exclamation"

    #: Extra CSS applied to all icons
    ICON_CSS_EXTRA: str = ""

    #: FontAwesome version used (default: 6)
    FONTAWESOME_VERSION: int = 6

    #: Base Bootstrap color - default: "btn-default"
    BTN_CSS_COLOR: str = "btn-default"

    #: Bootstrap extra CSS - default: "btn-sm"
    BTN_CSS_EXTRA: str = "btn-sm"

    # Base template path
    DEFAULT_TEMPLATE_PATH: str = "buttons/{package}/button.html"

    class Meta:
        """Metaclass for :class:`buttons.conf.ButtonsAppConf`."""

        prefix = "buttons"
