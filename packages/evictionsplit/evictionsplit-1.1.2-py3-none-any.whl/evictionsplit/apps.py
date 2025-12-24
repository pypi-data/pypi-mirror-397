from django.apps import AppConfig

from . import __version__


class EvictionSplitConfig(AppConfig):
    name = "evictionsplit"
    label = "evictionsplit"
    verbose_name = f"Eviction Split v{__version__}"
