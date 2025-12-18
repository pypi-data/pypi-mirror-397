from abc import ABC, abstractmethod

import logging
# Необязательный импорт dglog
try:
    import dglog
    LoggerType = logging.Logger | dglog.Logger
except ImportError:
    LoggerType = logging.Logger

class ConfigStorageBase(ABC):
    """Абстрактный класс для источника конфигов."""

    def __init__(self, auto_reload: bool = False, logger: LoggerType | None = None):
        self.auto_reload = auto_reload
        self.logger = logger or logging.getLogger("dgsettings")

    @abstractmethod
    def load(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def save(self, data: dict):
        raise NotImplementedError

    def supports_auto_reload(self) -> bool:
        """Поддерживает ли слой отслеживание изменений (например, для файлов)."""
        return self.auto_reload

    def has_changed(self) -> bool:
        """Есть ли изменения источника (например, обновился файл на диске)."""
        return False
