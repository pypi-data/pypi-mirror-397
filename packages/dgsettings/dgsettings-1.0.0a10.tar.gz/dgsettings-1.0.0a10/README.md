# dgsettings
Универсальный менеджер конфигураций Python-приложений с поддержкой версионирования  
- ✔️ Чтение и авто-перезагрузка YAML/JSON-файлов с поддержкой переменных среды и .env  
- ✔️ Хранение и обновление конфигов из различных источников: файлов, PostgreSQL, Redis  
- ✔️ **Версионирование конфигураций** — сохранение истории изменений и возможность загрузки конкретных версий
- ✔️ **Поддержка RedisJSON и dgredis** — автоматическое определение и использование оптимального формата хранения
- ✔️ Плагинная архитектура — легко расширяется под ваши нужды  
- ✔️ Работа с несколькими сервисами (service_name)
- ✔️ Легкая интеграция c любой средой (FastAPI, Celery, классические сервисы, микросервисы)
---
## Возможности
- **Settings**: Основной класс для работы с деревом конфигурации.
- **FileConfigStorage**: Файловое хранение с автоматическим обновлением при изменении.
- **DBConfigStorage**: Встроенная поддержка PostgreSQL и других СУБД через SQLAlchemy с версионированием, автоматическое создание таблицы с JSON-полями.
- **RedisConfigStorage**: Быстрый конфиг через Redis с поддержкой RedisJSON и dgredis.
- **check_reload()**: Позволяет легко реализовать "hot reload" настроек сервиса, если источник изменился.
---
## Установка
```bash
pip install dgsettings  # базовая версия
pip install dgsettings[redis]    # для Redis-хранилища
pip install dgsettings[db]       # для работы с БД (PostgreSQL)
pip install dgsettings[dgredis]  # для dgredis клиента
pip install dgsettings[all]      # полная установка
```
---
## Пример использования
#### Самый простой вариант: использование файлового слоя
```python
from dgsettings import Settings

settings = Settings(file_="config.yaml", env_file=".env")
db = settings.get("db")
print(db["user"])   # поддерживаются переменные окружения и .env-файлов: db_user: "%PGUSER%"

# Авто-перезагрузка (например, в цикле сервиса)
if settings.check_reload():
    print("Конфиг-файл изменился! Нужно обновить состояние приложения")
```
---
#### Использование с PostgreSQL (DBConfigStorage) с версионированием
```python
from dgsettings import Settings, DBConfigStorage
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@localhost:5432/mydb")

# Простой вариант с автосозданием таблицы
storage = DBConfigStorage(
    engine=engine,
    service_name='my_service',
    auto_reload=True,
    create_table=True  # автоматически создаст таблицу app_configs если её нет
)

settings = Settings(storage=storage)

# Сохранение создаёт новую версию
version = storage.save({'db_host': 'localhost', 'db_port': 5432})
print(f"Saved as version {version}")

# Загрузка конкретной версии
config_v1 = storage.load(version=1)

# Получение всех версий
versions = storage.get_versions()
print(f"Available versions: {versions}")

# Удаление старых версий
storage.delete_version(1)
```

#### Расширенный пример с кастомной таблицей
```python
from sqlalchemy import Table, MetaData

# Если нужна кастомная таблица
metadata = MetaData()
table = Table("custom_configs", metadata, autoload_with=engine)

storage = DBConfigStorage(
    engine=engine,
    table=table,
    key_column='app_name',
    value_column='json_data',
    version_column='version_num',
    service_name='my_service',
    auto_reload=True
)
```
---
#### Использование с Redis (RedisConfigStorage)
```python
from dgsettings import Settings, RedisConfigStorage
import redis

# Стандартный redis клиент
client = redis.Redis(host="localhost", decode_responses=True)

storage = RedisConfigStorage(
    redis_client=client,
    redis_key="config:myservice",
    ts_key="config:myservice:ts",  # для hot reload
    auto_reload=True,
    use_redis_json=True  # попытаться использовать RedisJSON если доступен
)

settings = Settings(storage=storage)

# Проверка используемого формата хранения
print(storage.get_storage_info())
# {'use_redis_json': True, 'storage_format': 'RedisJSON', 'is_dgredis': False}
```

#### Использование с dgredis (с автоматическим JSON)
```python
from dgsettings import Settings, RedisConfigStorage
import dgredis

# dgredis синхронный
dgredis_client = dgredis.RedisClient(host='localhost', port=6379, db=0)
storage = RedisConfigStorage(
    redis_client=dgredis_client,
    redis_key='config:myservice',
    use_redis_json=True  # dgredis поддерживает JSON нативно
)

# dgredis асинхронный
async_client = dgredis.AsyncRedisClient(host='localhost')
async_storage = RedisConfigStorage(
    redis_client=async_client,
    redis_key='config:myservice',
    use_redis_json=True
)

# Асинхронное использование
async def load_config():
    config = await async_storage.load()
    await async_storage.save({'new_setting': 'value'})
    changed = await async_storage.has_changed()
```
---
## API кратко
### Основные методы Settings
- `Settings(file_="...", env_file="...")` — создание и авто-парсинг конфига.
- `parse(file_)` — парсинг файла (JSON/YAML).
- `save(file_)` — сохранить текущий конфиг в файл.
- `get(key, default=None)` — получить значение по ключу.
- `set(obj)` — установить словарь настроек.
- `check_reload()` — если источник изменился, перезагружает, возвращает True.
- `convert("config.yaml", "config.json", use_yaml=False)` — переводит между форматами JSON/YAML.

### Методы DBConfigStorage с версионированием
- `load(version=None)` — загружает конкретную версию или последнюю.
- `save(data, increment_version=True)` — сохраняет с созданием новой версии или обновлением текущей.
- `get_versions()` — возвращает список всех доступных версий.
- `delete_version(version)` — удаляет конкретную версию.
- `get_current_version()` — возвращает номер текущей версии.

### Методы RedisConfigStorage
- `get_client_info()` — информация о типе клиента и формате хранения.
- `force_string_mode()` — принудительное переключение на строковое хранение.
- `retry_json_mode()` — попытка включить JSON режим.
- `clear_config()` — удаление конфигурации.
- `exists()` — проверка существования конфигурации.
---
## Переменные среды и .env
Любая строка вида `$VARNAME$` или `${VARNAME}` в конфиге подменяется на значение переменной среды или из файла .env

**.env:**
```
PGUSER=postgres
PGPASSWORD=secret
```

**config.yaml:**
```yaml
db_user: "$PGUSER$"
db_pass: "${PGPASSWORD}"
```
---
## Автосоздание таблицы PostgreSQL с JSON и версионированием
Таблица создаётся автоматически с оптимальной структурой:

```sql
CREATE TABLE app_configs (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(128) NOT NULL,
    config_data JSON NOT NULL,  -- JSON поле для эффективного хранения
    version INTEGER NOT NULL DEFAULT 1,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_app_configs_service_version ON app_configs(service_name, version);
```

```python
# Автосоздание таблицы
storage = DBConfigStorage(
    engine=engine,
    service_name='my_service',
    create_table=True  # создаст таблицу если не существует
)
```
---
## Поддержка различных Redis клиентов

### Автоматическое определение типа клиента:
- **redis-py**: Стандартный клиент с поддержкой RedisJSON модуля
- **dgredis**: Продвинутый клиент с нативной поддержкой JSON
- **Асинхронные клиенты**: aioredis, dgredis.AsyncRedisClient

### Автоматический выбор формата хранения:
- **RedisJSON**: Если установлен модуль RedisJSON на сервере
- **dgredis JSON**: Нативная поддержка JSON в dgredis
- **String fallback**: Автоматический откат к строковому формату

```python
# Проверка поддерживаемых возможностей
info = storage.get_client_info()
print(f"Client: {info['client_type']}")
print(f"Storage format: {info['storage_format']}")
print(f"Async support: {info['is_async']}")
```
---
## Необязательные зависимости
- **Базовая функциональность**: только PyYAML
- **БД (PostgreSQL)**: `sqlalchemy`, `psycopg2-binary` или `asyncpg`
- **Redis**: `redis-py` для стандартного клиента
- **dgredis**: `dgredis` для расширенного клиента
- **RedisJSON**: модуль RedisJSON на сервере для оптимального хранения

Если зависимости не установлены, соответствующий storage будет недоступен, но базовая функциональность остается рабочей.
---
## Пример сервисной интеграции с версионированием
```python
from dgsettings import Settings, DBConfigStorage
from sqlalchemy import create_engine

# Инициализация
engine = create_engine("postgresql://user:pass@localhost/db")
storage = DBConfigStorage(engine=engine, service_name='web_service', create_table=True)
settings = Settings(storage=storage)

# В основном коде приложения
class MyService:
    def __init__(self):
        self.settings = settings
        self.current_version = storage.get_current_version()
    
    def check_and_reload(self):
        """Проверка и перезагрузка конфигурации"""
        if self.settings.check_reload():
            new_version = storage.get_current_version()
            print(f"Config reloaded! Version: {self.current_version} -> {new_version}")
            self.current_version = new_version
            self.apply_new_settings()
            return True
        return False
    
    def rollback_to_version(self, version: int):
        """Откат к предыдущей версии"""
        config = storage.load(version=version)
        if config:
            self.settings.set(config)
            print(f"Rolled back to version {version}")

# В потоке/таймере/worker-e проверяем:
service = MyService()
if service.check_and_reload():
    print("Settings were updated!")
```
---
## Расширяемость
Вы можете реализовать свой storage (например, через S3, Consul, etcd).
Просто реализуйте абстрактный класс `ConfigStorageBase`:

```python
from dgsettings.storage import ConfigStorageBase

class MyCustomStorage(ConfigStorageBase):
    def load(self) -> dict:
        # Загрузка конфигурации из вашего источника
        pass
    
    def save(self, data: dict):
        # Сохранение конфигурации
        pass
    
    def has_changed(self) -> bool:
        # Проверка изменений для auto_reload
        pass
```
---
## Миграция конфигураций между версиями
```python
# Получение всех версий для анализа
versions = storage.get_versions()

for version in versions:
    config = storage.load(version=version)
    print(f"Version {version}: {list(config.keys())}")

# Создание новой версии на основе старой с изменениями
old_config = storage.load(version=1)
new_config = {**old_config, 'new_feature_enabled': True}
new_version = storage.save(new_config)
```
---
## Производительность и рекомендации

### Для PostgreSQL:
- Используйте JSON поля для эффективных запросов
- Регулярно очищайте старые версии конфигураций
- Настройте индексы для быстрого поиска по service_name

### Для Redis:
- Предпочитайте RedisJSON для сложных конфигураций
- Используйте dgredis для максимальной производительности
- Настройте TTL для временных конфигураций

### Общие рекомендации:
- Включайте `auto_reload=True` только при необходимости
- Используйте версионирование для критичных сервисов
- Настройте мониторинг изменений конфигураций
---
## Contributing
Пулреквесты, багрепорты и обсуждения приветствуются!

### Запуск тестов
```bash
# Установка dev зависимостей
pip install -e .[dev]

# Запуск тестов
pytest tests/

# Запуск с покрытием
pytest --cov=dgsettings tests/
```
---
## Лицензия
MIT
---
**Авторы:**  
Roman Rasputin
---
**Примеры, полная документация по API и архитектуре — см. исходный код и примеры в репозитории!**
