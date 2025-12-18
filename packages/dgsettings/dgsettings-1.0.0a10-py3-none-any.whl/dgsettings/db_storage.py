import json
from .storage import ConfigStorageBase
import logging
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

# Необязательный импорт dglog
try:
    import dglog

    LoggerType = logging.Logger | dglog.Logger
except ImportError:
    LoggerType = logging.Logger


class DBConfigStorage(ConfigStorageBase):
    @classmethod
    def create_table_if_needed(cls, engine, table_name="app_configs"):
        from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, func
        from sqlalchemy.dialects.postgresql import JSON
        from sqlalchemy.dialects.mysql import JSON as MySQL_JSON
        from sqlalchemy.dialects.sqlite import JSON as SQLite_JSON

        # Используем inspect для проверки существования таблицы
        inspector = inspect(engine)
        if not inspector.has_table(table_name):
            metadata = MetaData()

            # Определяем тип JSON поля в зависимости от диалекта БД
            dialect_name = engine.dialect.name.lower()
            if dialect_name == 'postgresql':
                json_type = JSON
            elif dialect_name == 'mysql':
                json_type = MySQL_JSON
            elif dialect_name == 'sqlite':
                json_type = SQLite_JSON
            else:
                # Для других БД используем Text как fallback
                from sqlalchemy import Text
                json_type = Text

            t = Table(
                table_name, metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('service_name', String(128), nullable=False, index=True),
                Column('config_data', json_type, nullable=False),
                Column('version', Integer, nullable=False, default=1),
                Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
            )
            # Создаем составной индекс для быстрого поиска по service_name + version
            from sqlalchemy import Index
            Index(f"ix_{table_name}_service_version", t.c.service_name, t.c.version)

            metadata.create_all(bind=engine, checkfirst=True)

    def __init__(self, engine=None, session_factory=None, table=None, key_column: str = "service_name",
                 value_column: str = "config_data", version_column: str = "version",
                 table_name: str = "app_configs", config_id=None, auto_reload: bool = False,
                 service_name: str = None, updated_at_column: str = "updated_at",
                 logger: LoggerType | None = None, create_table: bool = False,
                 config_version: int = None, use_json_field: bool = True):
        super().__init__(auto_reload=auto_reload, logger=logger)

        self.engine = engine
        self.config_id = config_id
        self.service_name = service_name
        self.updated_at_column = updated_at_column
        self.version_column = version_column
        self.config_version = config_version
        self.use_json_field = use_json_field  # Для совместимости с Text полями
        self._last_update = None
        self._current_version = None

        # Если session_factory не указана, создаем по умолчанию
        if session_factory is None:
            if engine is None:
                raise ValueError("Either session_factory or engine must be provided")
            Session = sessionmaker(bind=engine)
            self.session_factory = Session
        else:
            self.session_factory = session_factory

        # Если нужно создать таблицу
        if create_table:
            if engine is None:
                raise ValueError("Engine must be provided when create_table=True")

            # Определяем имя таблицы
            actual_table_name = table_name
            if table is not None and hasattr(table, '__tablename__'):
                actual_table_name = table.__tablename__

            self.create_table_if_needed(engine, actual_table_name)

        # Настройка таблицы и колонок
        if table is None:
            if engine is None:
                raise ValueError("Engine must be provided when table is None")

            from sqlalchemy import Table, MetaData
            metadata = MetaData()
            try:
                self.table = Table(table_name, metadata, autoload_with=engine)
                # Автоматически определяем, JSON ли поле
                config_column = getattr(self.table.c, value_column)
                self.use_json_field = self._is_json_column(config_column)
            except Exception as e:
                raise ValueError(f"Could not load default table '{table_name}'. "
                                 f"Either provide a table object or set create_table=True. Error: {e}")
        else:
            self.table = table
            if hasattr(table.c, value_column):
                config_column = getattr(table.c, value_column)
                self.use_json_field = self._is_json_column(config_column)

        self.key_column = key_column
        self.value_column = value_column

    def _is_json_column(self, column):
        """Определяет, является ли колонка JSON типом"""
        from sqlalchemy.dialects.postgresql import JSON
        from sqlalchemy.dialects.mysql import JSON as MySQL_JSON
        from sqlalchemy.dialects.sqlite import JSON as SQLite_JSON
        from sqlalchemy import Text

        column_type = column.type
        json_types = (JSON, MySQL_JSON, SQLite_JSON)

        # Проверяем класс типа
        return any(isinstance(column_type, json_type) for json_type in json_types)

    def _serialize_data(self, data: dict):
        """Сериализует данные в зависимости от типа поля"""
        if self.use_json_field:
            # Для JSON полей возвращаем dict как есть - SQLAlchemy сам сериализует
            return data
        else:
            # Для Text полей сериализуем в строку
            return json.dumps(data, ensure_ascii=False)

    def _deserialize_data(self, value):
        """Десериализует данные в зависимости от типа поля"""
        if self.use_json_field:
            # Для JSON полей данные уже десериализованы SQLAlchemy
            return value if isinstance(value, dict) else {}
        else:
            # Для Text полей парсим JSON
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return {}
            return value if isinstance(value, dict) else {}

    def _build_base_query(self, session):
        """Строит базовый запрос с фильтрами по service_name и config_id"""
        q = session.query(self.table)

        if self.config_id is not None and hasattr(self.table.c, 'id'):
            q = q.filter(self.table.c.id == self.config_id)

        if self.service_name and hasattr(self.table.c, self.key_column):
            q = q.filter(getattr(self.table.c, self.key_column) == self.service_name)

        return q

    def load(self, version: int = None) -> dict:
        """
        Загружает конфигурацию
        :param version: Номер версии для загрузки. Если None - загружается последняя версия
        """
        target_version = version or self.config_version

        with self.session_factory() as session:
            q = self._build_base_query(session)

            if target_version is not None:
                # Загружаем конкретную версию
                if hasattr(self.table.c, self.version_column):
                    q = q.filter(getattr(self.table.c, self.version_column) == target_version)
                row = q.first()
            else:
                # Загружаем последнюю версию
                if hasattr(self.table.c, self.version_column):
                    q = q.order_by(getattr(self.table.c, self.version_column).desc())
                else:
                    q = q.order_by(getattr(self.table.c, self.updated_at_column).desc())
                row = q.first()

            if not row:
                version_info = f" (version {target_version})" if target_version else ""
                self.logger.warning(f"No config found for service '{self.service_name}'{version_info}")
                return {}

            if hasattr(row, self.updated_at_column):
                self._last_update = getattr(row, self.updated_at_column)

            if hasattr(row, self.version_column):
                self._current_version = getattr(row, self.version_column)

            value = getattr(row, self.value_column)
            version_info = f" (version {self._current_version})" if self._current_version else ""
            self.logger.info(f"Config fetched successfully from database{version_info}")

            return self._deserialize_data(value)

    def save(self, data: dict, increment_version: bool = True) -> int:
        """
        Сохраняет конфигурацию
        :param data: Данные для сохранения
        :param increment_version: Увеличивать ли версию при сохранении
        :return: Номер версии сохраненного конфига
        """
        with self.session_factory() as session:
            value = self._serialize_data(data)

            if increment_version:
                # Получаем максимальную версию для данного сервиса
                q = self._build_base_query(session)
                if hasattr(self.table.c, self.version_column):
                    from sqlalchemy import func
                    max_version_result = q.with_entities(
                        func.max(getattr(self.table.c, self.version_column))
                    ).scalar()
                    next_version = (max_version_result or 0) + 1
                else:
                    next_version = 1

                # Создаем новую запись с новой версией
                insert_values = {
                    self.key_column: self.service_name,
                    self.value_column: value,
                }

                if hasattr(self.table.c, self.version_column):
                    insert_values[self.version_column] = next_version

                session.execute(self.table.insert().values(**insert_values))
                self._current_version = next_version

            else:
                # Обновляем существующую запись
                q = self._build_base_query(session)
                if self.config_version is not None and hasattr(self.table.c, self.version_column):
                    q = q.filter(getattr(self.table.c, self.version_column) == self.config_version)

                row = q.first()
                if row:
                    update_values = {self.value_column: value}
                    q.update(update_values)
                    if hasattr(row, self.version_column):
                        self._current_version = getattr(row, self.version_column)
                else:
                    # Создаем новую запись
                    insert_values = {
                        self.key_column: self.service_name,
                        self.value_column: value,
                    }
                    if hasattr(self.table.c, self.version_column):
                        insert_values[self.version_column] = self.config_version or 1
                        self._current_version = self.config_version or 1

                    session.execute(self.table.insert().values(**insert_values))

            session.commit()

            # Обновляем время последнего изменения
            q = self._build_base_query(session)
            if hasattr(self.table.c, self.version_column) and self._current_version:
                q = q.filter(getattr(self.table.c, self.version_column) == self._current_version)

            updated_row = q.first()
            if updated_row and hasattr(updated_row, self.updated_at_column):
                self._last_update = getattr(updated_row, self.updated_at_column)

            version_info = f" (version {self._current_version})" if self._current_version else ""
            self.logger.info(f"Config saved successfully to database{version_info}")

            return self._current_version or 1

    def has_changed(self) -> bool:
        if not self.auto_reload:
            return False

        target_version = self.config_version

        with self.session_factory() as session:
            q = self._build_base_query(session)

            if target_version is not None:
                if hasattr(self.table.c, self.version_column):
                    q = q.filter(getattr(self.table.c, self.version_column) == target_version)
            else:
                if hasattr(self.table.c, self.version_column):
                    q = q.order_by(getattr(self.table.c, self.version_column).desc())
                else:
                    q = q.order_by(getattr(self.table.c, self.updated_at_column).desc())

            row = q.first()
            if not row or not hasattr(row, self.updated_at_column):
                return False

            cur_update = getattr(row, self.updated_at_column)
            changed = cur_update != self._last_update
            if changed:
                self._last_update = cur_update
                if hasattr(row, self.version_column):
                    self._current_version = getattr(row, self.version_column)
            return changed

    def get_versions(self) -> list:
        """Возвращает список всех доступных версий для данного сервиса"""
        with self.session_factory() as session:
            q = self._build_base_query(session)

            if hasattr(self.table.c, self.version_column):
                versions = q.with_entities(
                    getattr(self.table.c, self.version_column)
                ).order_by(getattr(self.table.c, self.version_column).desc()).all()
                return [v[0] for v in versions]
            else:
                return []

    def get_current_version(self) -> int:
        """Возвращает номер текущей (последней) версии"""
        return self._current_version

    def delete_version(self, version: int) -> bool:
        """
        Удаляет конкретную версию конфигурации
        :param version: Номер версии для удаления
        :return: True если версия была удалена, False если не найдена
        """
        with self.session_factory() as session:
            q = self._build_base_query(session)

            if hasattr(self.table.c, self.version_column):
                q = q.filter(getattr(self.table.c, self.version_column) == version)

            result = q.delete()
            session.commit()
