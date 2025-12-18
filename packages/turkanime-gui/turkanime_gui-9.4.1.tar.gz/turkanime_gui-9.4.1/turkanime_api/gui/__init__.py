"""PyQt6 GUI modülü."""
from turkanime_api.version import __version__ as APP_VERSION


class UpdateManager:
    """GUI için otomatik güncelleme yönetim sistemi."""

    def __init__(self, parent_window, current_version=None, dosyalar=None):
        self.parent = parent_window

        # Eğer dışarıdan current_version gelmemişse, dahili APP_VERSION'ı kullan
        if current_version is None:
            current_version = APP_VERSION
