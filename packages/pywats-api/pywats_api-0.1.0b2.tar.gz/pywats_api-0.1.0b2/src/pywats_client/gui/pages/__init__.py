"""
GUI Pages module

Contains all page widgets for the main window.
"""

from .base import BasePage
from .setup import SetupPage
from .connection import ConnectionPage
from .proxy_settings import ProxySettingsPage
from .converters import ConvertersPage
from .location import LocationPage
from .sn_handler import SNHandlerPage
from .software import SoftwarePage
from .about import AboutPage
from .log import LogPage
from .asset import AssetPage
from .rootcause import RootCausePage
from .production import ProductionPage
from .product import ProductPage

__all__ = [
    "BasePage",
    "SetupPage",
    "ConnectionPage",
    "ProxySettingsPage",
    "ConvertersPage",
    "LocationPage",
    "SNHandlerPage",
    "SoftwarePage",
    "AboutPage",
    "LogPage",
    "AssetPage",
    "RootCausePage",
    "ProductionPage",
    "ProductPage",
]
