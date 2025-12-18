import itertools
import os
import yaml
import json

import logging
# Необязательный импорт dglog
try:
    import dglog
    LoggerType = logging.Logger | dglog.Logger
except ImportError:
    LoggerType = logging.Logger

from .errors import ConfigNotFoundError
from .storage import ConfigStorageBase


class FileConfigStorage(ConfigStorageBase):
    def __init__(self, filename: str, use_yaml: bool = True, encoding: str = 'utf-8', auto_reload: bool = True,
                 logger: LoggerType | None = None):
        super().__init__(auto_reload=auto_reload, logger=logger)
        self.filename = filename
        self.use_yaml = use_yaml
        self.encoding = encoding
        self.last_mtime = None

        self.file_extensions_allowed = ['json', 'yaml', 'yml', 'ini', 'cfg', 'conf']
        self.possible_file_names = ['settings', 'application', 'configs', 'config', ]

        if not self.exists(self.filename):
            self.filename = self.find_config(os.path.dirname(self.filename))

    def load(self) -> dict:
        with open(self.filename, encoding=self.encoding) as f:
            data = yaml.safe_load(f) if self.use_yaml else json.load(f)
        self.last_mtime = os.path.getmtime(self.filename)
        self.logger.info(f'Config loaded successfully from file: {self.filename}')
        return data

    def save(self, data: dict):
        with open(self.filename, 'w', encoding=self.encoding) as f:
            if self.use_yaml:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f'Config saved successfully to file: {self.filename}')
        self.last_mtime = os.path.getmtime(self.filename)

    def has_changed(self) -> bool:
        if not self.auto_reload:
            return False
        try:
            mtime = os.path.getmtime(self.filename)
            if self.last_mtime is None:
                self.last_mtime = mtime
                return False
            changed = mtime != self.last_mtime
            if changed:
                self.last_mtime = mtime
            return changed
        except Exception:
            return False

    def find_config(self, config_dir: str = '.'):
        possible_settings_file_names = [f"{a}.{b}" for a, b in itertools.product(self.possible_file_names, self.file_extensions_allowed)]
        for possible_file in possible_settings_file_names:
            for directory in (config_dir, '.'):
                if self.exists(os.path.join(directory, possible_file)):
                    self.logger.info(f'Found config file: {possible_file}')
                    return os.path.join(directory, possible_file)
        raise ConfigNotFoundError(f"There is no one of possible config files [{possible_settings_file_names}] in directories {config_dir} or in root")

    @staticmethod
    def exists(file_path: str):
        return os.path.exists(file_path)

    # ALIASES
    find_config_file = find_config
    config_file_exists = exists
